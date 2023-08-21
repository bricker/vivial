import assert from 'node:assert';
import { constants as httpConstants } from 'node:http2';
import { NextFunction, Request, Response, Router, raw, Express } from 'express';
import { createTaskFromRequest } from '@eave-fyi/eave-stdlib-ts/src/task-queue.js';
import verifyWebhookPayload from './verify-payload.js';
import { createAppClient } from '../lib/octokit-util.js';
import { LogContext } from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { GITHUB_EVENT_QUEUE_NAME, GITHUB_EVENT_QUEUE_TARGET_PATH } from '../config.js';
import { EaveOrigin } from '@eave-fyi/eave-stdlib-ts/src/eave-origins.js';
import { commonInternalApiMiddlewares, rawJsonBody } from '@eave-fyi/eave-stdlib-ts/src/middleware/common-middlewares.js';
import registry from './registry.js';
import parseAndValidateWebhookPayload from '../middleware/process-webhook-payload.js';
import { jsonParser } from '@eave-fyi/eave-stdlib-ts/src/middleware/body-parser.js';

export function WebhookRouter(): Router {
  const router = Router();
  /*
  Using raw parsing rather than express.json() parser because of GitHub signature verification.
  JSON.parse/stringify changes the bytes of the original body, so signature verification would fail.
  */
  router.use(rawJsonBody);
  router.use(parseAndValidateWebhookPayload);

  /*
    This is the endpoint that GitHub sends events to. It does the following:
    1. Validates the payload (via middleware)
    2. Gets the Eave Team associated with this event
    3. Passes the request off to the background queue
  */
  router.post('/', async (req: Request, res: Response, next: NextFunction) => {
    const ctx = LogContext.load(res);

    try {
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


  router.post('/_bg', async (req: Request, res: Response, next: NextFunction) => {
    try {
      const ctx = LogContext.load(res);
      const {
        parsedBody,
        fullEventName,
      } = parseWebhookPayload(req);

      const handler = registry[fullEventName];
      assert(handler);

      const app = await createAppClient();
      const octokit = await app.getInstallationOctokit(parsedBody.installation.id);
      await handler(parsedBody, { octokit, ctx });
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });
  return router;
}

export function TaskQueueRouter(): Router {
  const router = Router();
  router.use(commonInternalApiMiddlewares, parseAndValidateWebhookPayload, jsonParser);
  router.use(parseAndValidateWebhookPayload);

  router.post('/events', async (req: Request, res: Response, next: NextFunction) => {
    try {
      const ctx = LogContext.load(res);
      const {
        parsedBody,
        fullEventName,
      } = parseWebhookPayload(req);

      const handler = registry[fullEventName];
      assert(handler);

      const app = await createAppClient();
      const octokit = await app.getInstallationOctokit(parsedBody.installation.id);
      await handler(parsedBody, { octokit, ctx });
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  return router;
}
