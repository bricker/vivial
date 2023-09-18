import assert from 'node:assert';
import { constants as httpConstants } from 'node:http2';
import Express from 'express';
import { createTaskFromRequest } from '@eave-fyi/eave-stdlib-ts/src/task-queue.js';
import eaveLogger, { LogContext } from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { EaveApp } from '@eave-fyi/eave-stdlib-ts/src/eave-origins.js';
import { GithubEventHandlerTaskOperation } from '@eave-fyi/eave-stdlib-ts/src/github-api/operations/event-handler-task.js';
import getCacheClient, { Cache } from '@eave-fyi/eave-stdlib-ts/src/cache.js';
import { rawJsonBody } from '@eave-fyi/eave-stdlib-ts/src/middleware/common-middlewares.js';
import { jsonParser } from '@eave-fyi/eave-stdlib-ts/src/middleware/body-parser.js';
import { getTeamForInstallation, githubAppClient } from '../lib/octokit-util.js';
import { GITHUB_EVENT_QUEUE_NAME } from '../config.js';
import registry, { HandlerFunction } from './registry.js';
import { GithubWebhookBody, getGithubWebhookHeaders, validateGithubWebhookHeaders } from '../middleware/process-webhook-payload.js';

function getEventHandler(req: Express.Request, res: Express.Response): HandlerFunction | undefined {
  const ctx = LogContext.load(res);
  const { eventName } = getGithubWebhookHeaders(req);
  const { action } = <GithubWebhookBody>req.body;
  const fullEventName = [eventName, action].filter((n) => n).join('.');

  const handler = registry[fullEventName];
  if (!handler) {
    eaveLogger.warning(`Event not supported: ${fullEventName}`, ctx);
  }

  return handler;
}

export function WebhookRouter(): Express.Router {
  const router = Express.Router();
  /*
  Using raw parsing rather than express.json() parser because of GitHub signature verification.
  JSON.parse/stringify changes the bytes of the original body, so signature verification would fail.
  */

  /*
    This is the endpoint that GitHub sends events to.
  */
  router.post('/github/events', rawJsonBody, validateGithubWebhookHeaders, jsonParser, async (req: Express.Request, res: Express.Response, next: Express.NextFunction) => {
    try {
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
        eaveLogger.warning('Error connecting to cache', ctx, e);
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
    } catch (e: unknown) {
      next(e);
    }
  });

  return router;
}

export function WebhookOfflineTaskRouter(): Express.Router {
  const router = Express.Router();

  router.post(GithubEventHandlerTaskOperation.config.path, ...GithubEventHandlerTaskOperation.config.middlewares, async (req: Express.Request, res: Express.Response, next: Express.NextFunction) => {
    try {
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
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  return router;
}
