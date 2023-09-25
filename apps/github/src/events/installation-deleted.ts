import { logEvent } from "@eave-fyi/eave-stdlib-ts/src/analytics.js";
import { InstallationDeletedEvent } from "@octokit/webhooks-types";
import { GitHubOperationsContext } from "../types.js";

/**
 * Receives github webhook installation events.
 * https://docs.github.com/en/webhooks/webhook-events-and-payloads?actionType=deleted#installation
 *
 * Features:
 * Remove the github_installation db entry for the Eave team that uninstalled the Eave GitHub app.
 * Also removes their github_repos and github_documents db entries; as if they never installed the app.
 */
export default async function handler(event: InstallationDeletedEvent, context: GitHubOperationsContext) {
  if (event.action !== "deleted") {
    return;
  }
  const { ctx } = context;

  await logEvent(
    {
      event_name: "github_app_installation_deleted",
      event_description: "An Eave team uninstalled the Eave GitHub app from their user/org",
      event_source: "github webhook installation.deleted event",
    },
    ctx,
  );

  // TODO: delete gh installation (how??? creat api endpoint?? exposure???)

  // TODO: delete gh_repos (if not already cascaded???)
  // gh_documents deletion will cascade from repo deletions
}
