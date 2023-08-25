import assert from 'node:assert';
import { constants as httpConstants } from 'node:http2';
import Express from 'express';
import { createTaskFromRequest } from '@eave-fyi/eave-stdlib-ts/src/task-queue.js';
import { getTeamForInstallation, githubAppClient } from '../lib/octokit-util.js';
import eaveLogger, { LogContext } from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { GITHUB_EVENT_QUEUE_NAME, GITHUB_EVENT_QUEUE_TARGET_PATH } from '../config.js';
import { EaveOrigin } from '@eave-fyi/eave-stdlib-ts/src/eave-origins.js';
import { commonInternalApiMiddlewares, rawJsonBody } from '@eave-fyi/eave-stdlib-ts/src/middleware/common-middlewares.js';
import registry, { HandlerFunction } from './registry.js';
import { GithubWebhookBody, getGithubWebhookHeaders, validateGithubWebhookHeaders } from '../middleware/process-webhook-payload.js';
import { jsonParser } from '@eave-fyi/eave-stdlib-ts/src/middleware/body-parser.js';

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
  router.use(rawJsonBody);
  router.use(validateGithubWebhookHeaders);
  router.use(jsonParser);

  /*
    This is the endpoint that GitHub sends events to.
  */
  router.post('/', async (req: Express.Request, res: Express.Response, next: Express.NextFunction) => {
    try {
      const ctx = LogContext.load(res);

      // Quick check to make sure we have a handler for this event.
      // No use creating a background task if we know it won't do anything.
      const handler = getEventHandler(req, res);
      if (!handler) {
        res.sendStatus(httpConstants.HTTP_STATUS_OK);
        return;
      }

      const eventBody = <GithubWebhookBody>req.body;
      const installationId = eventBody.installation.id;
      const eaveTeam = await getTeamForInstallation({ installationId, ctx });

      if (!eaveTeam) {
        eaveLogger.warning(`No Eave Team found for installation ID ${installationId}`, ctx, { installationId });
        res.sendStatus(httpConstants.HTTP_STATUS_FORBIDDEN);
        return;
      }

      ctx.eave_team_id = eaveTeam.id;

      await createTaskFromRequest({
        queueName: GITHUB_EVENT_QUEUE_NAME,
        targetPath: GITHUB_EVENT_QUEUE_TARGET_PATH,
        origin: EaveOrigin.eave_github_app,
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

export function TaskQueueRouter(): Express.Router {
  const router = Express.Router();
  router.use(commonInternalApiMiddlewares);
  // github webhook signature assumed to be already verified.
  router.use(jsonParser);

  router.post('/events', async (req: Express.Request, res: Express.Response, next: Express.NextFunction) => {
    try {
      const ctx = LogContext.load(res);
      const handler = getEventHandler(req, res);
      if (!handler) {
        res.sendStatus(httpConstants.HTTP_STATUS_OK);
        return;
      }

      const eventBody = <GithubWebhookBody>req.body;
      const app = await githubAppClient();
      const octokit = await app.getInstallationOctokit(eventBody.installation.id);
      await handler(eventBody, { octokit, ctx });
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  return router;
}
