import { LifecycleRouter } from '@eave-fyi/eave-stdlib-ts/src/connect/lifecycle-router.js';
import { AtlassianProduct } from '@eave-fyi/eave-stdlib-ts/src/core-api/models/connect.js';
import { AddOn } from 'atlassian-connect-express';
import express, { Request, Response, Router, Express } from 'express';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import appConfig from '../config.js';

export function applyWebhookMiddlewares({ app, addon, path }: {app: Express, addon: AddOn, path: string}) {
  app.use(path, express.json());
  app.use(path, addon.middleware());
}

export function WebhookRouter({ addon }: { addon: AddOn }): Router {
  // webhooks
  const router = Router();

  const lifecycleRouter = LifecycleRouter({ addon, product: AtlassianProduct.confluence, eaveOrigin: appConfig.eaveOrigin });
  router.use(lifecycleRouter);

  router.post('/', addon.authenticate(), async (req: Request, _res: Response) => {
    eaveLogger.info('received webhook event', { body: req.body, headers: req.headers });
  });

  return router;
}
