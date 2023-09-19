import { InstallationRepositoriesAddedEvent } from '@octokit/webhooks-types';
import { createGithubRepo, getGithubRepos, queryGithubReposFeatureState } from '@eave-fyi/eave-stdlib-ts/src/core-api/operations/github-repos.js'
import { EaveApp } from '@eave-fyi/eave-stdlib-ts/src/eave-origins.js';
import { Feature, State } from '@eave-fyi/eave-stdlib-ts/src/core-api/models/github-repos.js';
import { enumCases } from '@eave-fyi/eave-stdlib-ts/src/util.js';
import { RunApiDocumentationTaskOperation } from '@eave-fyi/eave-stdlib-ts/src/github-api/operations/run-api-documentation-task.js';
import { GitHubOperationsContext } from '../types.js';

/**
 * Receives github webhook pull_request events.
 * https://docs.github.com/en/webhooks/webhook-events-and-payloads#installation_repositories
 *
 * Features:
 * Inserts rows into the github_repos db table with feature activation states matching
 * the other rows in the table whenever it is given access to new repos in GitHub.
 */
export default async function handler(event: InstallationRepositoriesAddedEvent, context: GitHubOperationsContext) {
  if (event.action !== 'added') {
    return;
  }
  const { ctx } = context;

  const sharedReqInput = {
    teamId: ctx.eave_team_id,
    origin: EaveApp.eave_github_app,
    ctx,
  };

  const res = await getGithubRepos({
    ...sharedReqInput,
    input: {}
  });
  if (res.repos.length < 1) {
    // exit early; website app handles adding first repo(s) to the db
    return;
  }

  for (const repo of event.repositories_added) {
    const defaultFeatureStates: { [key: string]: State } = {}

    for (const feat of enumCases(Feature)) {
      // TODO: don't skip arch feature once implemented
      if (feat === Feature.ARCHITECTURE_DOCUMENTATION) {
        continue;
      }

      // if all the team's repos have the ENABLED state for this feature,
      // the new repo will also get the ENABLED state to match the default
      defaultFeatureStates[feat] = (await queryGithubReposFeatureState({
        ...sharedReqInput,
        input: {
          query_params: {
            feature: feat,
            state: State.ENABLED,
          }
        }
      })).states_match ? State.ENABLED : State.DISABLED;
    }

    const repoResponse = await createGithubRepo({
      teamId: ctx.eave_team_id,
      origin: EaveApp.eave_confluence_app,
      input: {
        repo: {
          external_repo_id: repo.node_id,
          api_documentation_state: defaultFeatureStates[Feature.API_DOCUMENTATION] || State.DISABLED,
          inline_code_documentation_state: defaultFeatureStates[Feature.INLINE_CODE_DOCUMENTATION] || State.DISABLED,
          architecture_documentation_state: defaultFeatureStates[Feature.ARCHITECTURE_DOCUMENTATION] || State.DISABLED,
        }
      },
    });

    // run api docs for first time if necessary
    if (repoResponse.repo.api_documentation_state === State.ENABLED) {
      await RunApiDocumentationTaskOperation.perform({
        ...sharedReqInput,
        input: {
          repo: {
            external_repo_id: repoResponse.repo.external_repo_id,
          }
        },
      });
    }
  }
}
