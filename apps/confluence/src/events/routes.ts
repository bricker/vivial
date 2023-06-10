import { LifecycleRouter } from "@eave-fyi/eave-stdlib-ts/src/connect/lifecycle-router.js";
import { AtlassianProduct } from "@eave-fyi/eave-stdlib-ts/src/core-api/models/connect.js";
import { AddOn } from "atlassian-connect-express";
import express, { Request, RequestHandler, Response, Router } from "express";
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import appConfig from "../config.js";

export function webhookMiddlewares({addon}: {addon: AddOn}): RequestHandler[] {
  return [
    express.json(),
    addon.middleware(),
  ];
}

export function WebhookRouter({ addon }: { addon: AddOn }): Router {
  // webhooks
  const webhookRouter = Router();

  const lifecycleRouter = LifecycleRouter({ addon, product: AtlassianProduct.confluence, eaveOrigin: appConfig.eaveOrigin });
  webhookRouter.use(lifecycleRouter);

  webhookRouter.post('/', addon.authenticate(), async (req: Request, res: Response) => {
    eaveLogger.info('received webhook event', { body: req.body, headers: req.headers });
  });

  return webhookRouter;
}
