import { LogContext } from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import { assertPresence } from "@eave-fyi/eave-stdlib-ts/src/util.js";
import Express from "express";
import { constants as httpConstants } from "node:http2";
import {
  getTeamForInstallation,
  githubAppClient,
} from "../lib/octokit-util.js";
import {
  GithubWebhookBody,
  getEventHandler,
} from "../middleware/process-webhook-payload.js";

export async function webhookEventTaskHandler(
  req: Express.Request,
  res: Express.Response,
): Promise<void> {
  const ctx = LogContext.load(res);
  const handler = getEventHandler(req, res);
  if (!handler) {
    res.sendStatus(httpConstants.HTTP_STATUS_OK);
    return;
  }

  // FIXME: event.installation not available when using local webhook forwarding
  const event = <GithubWebhookBody>req.body;
  const installationId = event.installation.id;
  const eaveTeam = await getTeamForInstallation({ installationId, ctx });
  assertPresence(eaveTeam);

  ctx.eave_team_id = eaveTeam.id;

  const app = await githubAppClient();
  const octokit = await app.getInstallationOctokit(installationId);
  await handler({ event: event, eaveTeam, octokit, ctx });
}
