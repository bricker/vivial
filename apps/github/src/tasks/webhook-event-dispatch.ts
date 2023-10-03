import { MissingRequiredHeaderError } from "@eave-fyi/eave-stdlib-ts/src/exceptions.js";
import { LogContext } from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import Express from "express";
import { constants as httpConstants } from "node:http2";
import { githubAppClient } from "../lib/octokit-util.js";
import {
  GithubWebhookBody,
  getEventHandler,
  getGithubWebhookHeaders,
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

  const eventBody = <GithubWebhookBody>req.body;
  const installationId = eventBody.installation.id;

  const app = await githubAppClient();
  const octokit = await app.getInstallationOctokit(installationId);
  await handler(eventBody, { octokit, ctx });
}
