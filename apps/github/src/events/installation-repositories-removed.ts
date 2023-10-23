import {
  DeleteGithubRepoOperation,
  GetGithubReposOperation,
} from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/github-repos.js";
import { InstallationRepositoriesRemovedEvent } from "@octokit/webhooks-types";
import { appConfig } from "../config.js";
import { EventHandlerArgs } from "../types.js";

/**
 * Handles the removal of installation repositories from GitHub webhook installation_repositories.removed events.
 * https://docs.github.com/en/webhooks/webhook-events-and-payloads#installation_repositories
 * If the event action is not 'removed', the function will return without performing any operations.
 * Otherwise, it fetches the repositories to be deleted and performs the deletion operation, removing entries from github_repos DB table that we no longer have permission to access through the GitHub API.
 *
 * @param {Object} args - The arguments for the event handler.
 * @param {InstallationRepositoriesRemovedEvent} args.event - The event object containing the repositories to be removed.
 * @param {Object} args.ctx - The context object.
 * @param {Object} args.eaveTeam - The Eave team object.
 *
 * @returns {Promise<void>} A promise that resolves when the operation is complete.
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
