import { logEvent } from "@eave-fyi/eave-stdlib-ts/src/analytics.js";
import { DeleteGithubInstallationOperation } from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/github.js";
import { EaveApp } from "@eave-fyi/eave-stdlib-ts/src/eave-origins.js";
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
export default async function handler(
  event: InstallationDeletedEvent,
  context: GitHubOperationsContext,
) {
  if (event.action !== "deleted") {
    return;
  }
  const { ctx } = context;

  await logEvent(
    {
      event_name: "github_app_installation_deleted",
      event_description:
        "An Eave team uninstalled the Eave GitHub app from their user/org",
      event_source: "github webhook installation.deleted event",
    },
    ctx,
  );

  const sharedInput = {
    teamId: ctx.eave_team_id,
    origin: EaveApp.eave_github_app,
  };

  // remove gh app installation from user's eave account
  // (this will cascade delete all related github_repos and github_documents entries)
  await DeleteGithubInstallationOperation.perform({
    ...sharedInput,
    input: {
      github_integration: {
        github_install_id: event.installation.id.toString(),
      },
    },
  });
}
