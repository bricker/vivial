import {
  Feature,
  State,
} from "@eave-fyi/eave-stdlib-ts/src/core-api/models/github-repos.js";
import { Team } from "@eave-fyi/eave-stdlib-ts/src/core-api/models/team.js";
import {
  CreateGithubRepoOperation,
  FeatureStateGithubReposOperation,
  GetGithubReposOperation,
} from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/github-repos.js";
import { EaveApp } from "@eave-fyi/eave-stdlib-ts/src/eave-origins.js";
import { RunApiDocumentationTaskOperation } from "@eave-fyi/eave-stdlib-ts/src/github-api/operations/run-api-documentation-task.js";
import { CtxArg } from "@eave-fyi/eave-stdlib-ts/src/requests.js";
import { enumCases } from "@eave-fyi/eave-stdlib-ts/src/util.js";
import { InstallationRepositoriesAddedEvent } from "@octokit/webhooks-types";
import { EventHandlerArgs } from "../types.js";

/**
 * Receives github webhook installation_repositories events.
 * https://docs.github.com/en/webhooks/webhook-events-and-payloads#installation_repositories
 *
 * Features:
 * Inserts rows into the github_repos db table with feature activation states matching
 * the other rows in the table whenever it is given access to new repos in GitHub.
 */
export default async function handler({
  event,
  ctx,
  eaveTeam,
}: EventHandlerArgs & {
  event: InstallationRepositoriesAddedEvent;
}) {
  if (event.action !== "added") {
    return;
  }

  await maybeAddReposToDataBase({ event, ctx, eaveTeam });
}

export async function maybeAddReposToDataBase({
  event,
  ctx,
  eaveTeam,
}: CtxArg & { eaveTeam: Team; event: InstallationRepositoriesAddedEvent }) {
  const sharedReqInput = {
    teamId: eaveTeam.id,
    origin: EaveApp.eave_github_app,
    ctx,
  };

  const res = await GetGithubReposOperation.perform({
    ...sharedReqInput,
    input: {},
  });

  if (res.repos.length < 1) {
    // exit early; website app handles adding first repo(s) to the db
    return;
  }

  for (const repo of event.repositories_added) {
    const defaultFeatureStates: { [key: string]: State } = {};

    for (const feat of enumCases(Feature)) {
      // TODO: don't skip arch feature once implemented
      if (feat === Feature.ARCHITECTURE_DOCUMENTATION) {
        continue;
      }

      // if all the team's repos have the ENABLED state for this feature,
      // the new repo will also get the ENABLED state to match the default
      defaultFeatureStates[feat] = (
        await FeatureStateGithubReposOperation.perform({
          ...sharedReqInput,
          input: {
            query_params: {
              feature: feat,
              state: State.ENABLED,
            },
          },
        })
      ).states_match
        ? State.ENABLED
        : State.DISABLED;
    }

    const repoResponse = await CreateGithubRepoOperation.perform({
      ...sharedReqInput,
      input: {
        repo: {
          external_repo_id: repo.node_id,
          display_name: repo.name,
          api_documentation_state:
            defaultFeatureStates[Feature.API_DOCUMENTATION] || State.DISABLED,
          inline_code_documentation_state:
            defaultFeatureStates[Feature.INLINE_CODE_DOCUMENTATION] ||
            State.DISABLED,
          architecture_documentation_state:
            defaultFeatureStates[Feature.ARCHITECTURE_DOCUMENTATION] ||
            State.DISABLED,
        },
      },
    });

    // run api docs for first time if necessary
    if (repoResponse.repo.api_documentation_state === State.ENABLED) {
      await RunApiDocumentationTaskOperation.perform({
        ...sharedReqInput,
        input: {
          repo: {
            external_repo_id: repoResponse.repo.external_repo_id,
          },
        },
      });
    }
  }
}
