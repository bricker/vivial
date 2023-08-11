import { NextFunction, Request, Response, Router, raw, Express } from 'express';
import * as Registry from './registry.js';
import pushHandler from './push.js';
import verifyWebhookPayload from './verify.js';

Registry.registerHandler('push', pushHandler);

export function applyWebhookMiddlewares({ app, path }:{ app: Express, path: string }) {
  /*
  Using raw parsing rather than express.json() parser because of GitHub signature verification.
  If even 1 byte were different after passing through JSON.parse and then the signature verification would fail.
  */
  app.use(path, raw({ type: 'application/json', limit: '5mb' }));
  app.use(path, verifyWebhookPayload);
}

export function WebhookRouter(): Router {
  const router = Router();

  router.post('/', async (req: Request, res: Response, next: NextFunction) => {
    try {
      const octokit = await app.getInstallationOctokit(payload.installation.id);
      await handler(payload, { octokit, ctx });

      await dispatch(req, res);
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  return router;
}
