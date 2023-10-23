import {
  DeleteGithubRepoOperation,
  GetGithubReposOperation,
} from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/github-repos.js";
import { InstallationRepositoriesRemovedEvent } from "@octokit/webhooks-types";
import { appConfig } from "../config.js";
import { EventHandlerArgs } from "../types.js";

/**
 * Receives github webhook installation_repositories.removed events.
 * https://docs.github.com/en/webhooks/webhook-events-and-payloads#installation_repositories
 *
 * Features:
 * Removes entries from github_repos DB table that we no longer have permission to access
 * through the GitHub API.
 */
export default async function handler({
  event,
  ctx,
  eaveTeam,
}: EventHandlerArgs & {
  event: InstallationRepositoriesRemovedEvent;
}) {
  if (event.action !== "removed") {
    return;
  }

  const sharedReqInput = {
    teamId: eaveTeam.id,
    origin: appConfig.eaveOrigin,
    ctx,
  };

  // fetch the repos to delete
  const res = await GetGithubReposOperation.perform({
    ...sharedReqInput,
    input: {
      repos: event.repositories_removed.map((repo) => {
        return { external_repo_id: repo.id.toString() };
      }),
    },
  });

  await DeleteGithubRepoOperation.perform({
    ...sharedReqInput,
    input: {
      repos: res.repos.map((repo) => {
        return { id: repo.id };
      }),
    },
  });
}
