import { Team } from "@eave-fyi/eave-stdlib-ts/src/core-api/models/team.js";
import {
  EmitterWebhookEvent,
  EmitterWebhookEventName,
} from "@octokit/webhooks";
import { GitHubOperationsContext } from "../types.js";
import installationDeletedHandler from "./installation-deleted.js";
import installationRepoAddedHandler from "./installation-repositories-added.js";
import pullRequestClosedHandler from "./pull-request-closed.js";
import pushHandler from "./push.js";

export type HandlerFunction = (
  args: GitHubOperationsContext & {
    event: EmitterWebhookEvent<EmitterWebhookEventName> & any;
    eaveTeam: Team;
  },
) => Promise<void>;

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
    case "installation.deleted":
      return installationDeletedHandler;
    default:
      return undefined;
  }
}
