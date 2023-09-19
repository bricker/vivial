import { constants as httpConstants } from 'node:http2';
import Express from 'express';
import { LogContext } from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { RunApiDocumentationTaskOperation } from '@eave-fyi/eave-stdlib-ts/src/github-api/operations/run-api-documentation-task.js';
import { runApiDocumentation } from './api-documentation.js';
import { GithubEventHandlerTaskOperation } from '@eave-fyi/eave-stdlib-ts/src/github-api/operations/event-handler-task.js';
import { GithubWebhookBody, getEventHandler, getGithubWebhookHeaders } from '../middleware/process-webhook-payload.js';
import assert from 'node:assert';
import { githubAppClient } from '../lib/octokit-util.js';

export function OfflineTaskRouter(): Express.Router {
  const router = Express.Router();

  router.post(RunApiDocumentationTaskOperation.config.subPath, ...RunApiDocumentationTaskOperation.config.middlewares, async (req: Express.Request, res: Express.Response, next: Express.NextFunction) => {
    try {
      const ctx = LogContext.load(res);
      await runApiDocumentation({ req, res, ctx });
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  router.post(GithubEventHandlerTaskOperation.config.subPath, ...GithubEventHandlerTaskOperation.config.middlewares, async (req: Express.Request, res: Express.Response, next: Express.NextFunction) => {
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