import Express from "express";
import { constants as httpConstants } from 'node:http2';
import { LogContext } from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import { NextFunction } from "express";
import { GithubWebhookBody, getEventHandler, getGithubWebhookHeaders } from "../middleware/process-webhook-payload.js";
import assert from "node:assert";
import { githubAppClient } from "../lib/octokit-util.js";

export async function webhookEventTaskHandler(req: Express.Request, res: Express.Response): Promise<void> {
  const ctx = LogContext.load(res);
  const handler = getEventHandler(req, res);
  if (!handler) {
    res.sendStatus(httpConstants.HTTP_STATUS_OK);
    return;
  }

  const { installationId } = getGithubWebhookHeaders(req);
  assert(installationId);

  const eventBody = <GithubWebhookBody>req.body;
  const app = await githubAppClient();
  const octokit = await app.getInstallationOctokit(parseInt(installationId, 10));
  await handler(eventBody, { octokit, ctx });
}
