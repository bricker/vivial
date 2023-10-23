import { Team } from "@eave-fyi/eave-stdlib-ts/src/core-api/models/team.js";
import {
  EmitterWebhookEvent,
  EmitterWebhookEventName,
} from "@octokit/webhooks";
import { GitHubOperationsContext } from "../types.js";
import installationDeletedHandler from "./installation-deleted.js";
import installationRepoAddedHandler from "./installation-repositories-added.js";
import installationRepoRemovedHandler from "./installation-repositories-removed.js";
import pullRequestClosedHandler from "./pull-request-closed.js";
import pushHandler from "./push.js";

export type HandlerFunction = (
  args: GitHubOperationsContext & {
    event: EmitterWebhookEvent<EmitterWebhookEventName> & any;
    eaveTeam: Team;
  },
) => Promise<void>;

/**
 * Retrieves the appropriate event handler based on the provided dispatch key.
 * The keys correspond to GitHub events. A dictionary isn't used to avoid remote-code execution type attacks.
 *
 * @param {Object} param0 - An object containing the dispatch key.
 * @param {string} param0.dispatchKey - The dispatch key associated with a GitHub event.
 * @returns {HandlerFunction | undefined} The corresponding event handler function or undefined if no match is found.
 */
export function getEventHandler({
  dispatchKey,
}: {
  dispatchKey: string;
}): HandlerFunction | undefined {
  // These keys correspond to the github events
  // A dict isn't used to avoid remote-code execution type attacks, eg `eventRegistry[headerValue]`
  switch (dispatchKey) {
    case "push":
      return pushHandler;
    case "pull_request.closed":
      return pullRequestClosedHandler;
    case "installation_repositories.added":
      return installationRepoAddedHandler;
    case "installation_repositories.removed":
      return installationRepoRemovedHandler;
    case "installation.deleted":
      return installationDeletedHandler;
    default:
      return undefined;
  }
}
