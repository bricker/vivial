import { Cache, getCacheClient } from "@eave-fyi/eave-stdlib-ts/src/cache.js";
import { EaveApp } from "@eave-fyi/eave-stdlib-ts/src/eave-origins.js";
import { GithubEventHandlerTaskOperation } from "@eave-fyi/eave-stdlib-ts/src/github-api/operations/event-handler-task.js";
import {
  LogContext,
  eaveLogger,
} from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import { createTaskFromRequest } from "@eave-fyi/eave-stdlib-ts/src/task-queue.js";
import Express from "express";
import { constants as httpConstants } from "node:http2";
import { GITHUB_EVENT_QUEUE_NAME } from "../config.js";
import { getTeamForInstallation } from "../lib/octokit-util.js";
import {
  GithubWebhookBody,
  getEventHandler,
} from "../middleware/process-webhook-payload.js";

export async function webhookEventHandler(
  req: Express.Request,
  res: Express.Response,
): Promise<void> {
  const ctx = LogContext.load(res);

  // Quick check to make sure we have a handler for this event.
  // No use creating a background task if we know it won't do anything.
  const handler = getEventHandler(req, res);
  if (!handler) {
    res.sendStatus(httpConstants.HTTP_STATUS_OK);
    return;
  }

  await createTaskFromRequest({
    queueName: GITHUB_EVENT_QUEUE_NAME,
    targetPath: GithubEventHandlerTaskOperation.config.path,
    origin: EaveApp.eave_github_app,
    audience: EaveApp.eave_github_app,
    teamId: eaveTeamId,
    req,
    ctx,
  });

  res.sendStatus(httpConstants.HTTP_STATUS_OK);
}
