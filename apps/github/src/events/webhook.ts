import { Cache, getCacheClient } from "@eave-fyi/eave-stdlib-ts/src/cache.js";
import { EaveApp } from "@eave-fyi/eave-stdlib-ts/src/eave-origins.js";
import { GithubEventHandlerTaskOperation } from "@eave-fyi/eave-stdlib-ts/src/github-api/operations/event-handler-task.js";
import { eaveLogger, LogContext } from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import { createTaskFromRequest } from "@eave-fyi/eave-stdlib-ts/src/task-queue.js";
import Express from "express";
import assert from "node:assert";
import { constants as httpConstants } from "node:http2";
import { GITHUB_EVENT_QUEUE_NAME } from "../config.js";
import { getTeamForInstallation } from "../lib/octokit-util.js";
import { getEventHandler, getGithubWebhookHeaders } from "../middleware/process-webhook-payload.js";

export async function webhookEventHandler(req: Express.Request, res: Express.Response): Promise<void> {
  const ctx = LogContext.load(res);

  // Quick check to make sure we have a handler for this event.
  // No use creating a background task if we know it won't do anything.
  const handler = getEventHandler(req, res);
  if (!handler) {
    res.sendStatus(httpConstants.HTTP_STATUS_OK);
    return;
  }

  // event.installation not available when using local webhook forwarding, so we pull it from headers.
  const { installationId } = getGithubWebhookHeaders(req);
  // This was already validated present in the validateGithubWebhookHeaders middleware. This check is for the type checker, plus adds additional safety so the cache key isn't malformed and returns incorrect data.
  assert(installationId);

  const cacheKey = `github_installation:${installationId}:eave_team_id`;

  let eaveTeamId: string | undefined;
  let cacheClient: Cache | undefined;

  try {
    cacheClient = await getCacheClient();
    const cachedTeamId = await cacheClient.get(cacheKey);
    if (cachedTeamId) {
      eaveTeamId = cachedTeamId.toString();
    }
  } catch (e: any) {
    eaveLogger.warning("Error connecting to cache", ctx, e);
  }

  if (!eaveTeamId) {
    const eaveTeam = await getTeamForInstallation({ installationId, ctx });
    if (eaveTeam) {
      eaveTeamId = eaveTeam.id;
      if (cacheClient) {
        await cacheClient.set(cacheKey, eaveTeamId);
      }
    }
  }

  if (!eaveTeamId) {
    eaveLogger.warning(`No Eave Team found for installation ID ${installationId}`, ctx, { installationId });
    res.sendStatus(httpConstants.HTTP_STATUS_FORBIDDEN);
    return;
  }

  ctx.eave_team_id = eaveTeamId;

  await createTaskFromRequest({
    queueName: GITHUB_EVENT_QUEUE_NAME,
    targetPath: GithubEventHandlerTaskOperation.config.path,
    origin: EaveApp.eave_github_app,
    req,
    ctx,
  });

  res.sendStatus(httpConstants.HTTP_STATUS_OK);
}
