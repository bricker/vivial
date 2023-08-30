import { LifecycleRouter } from '@eave-fyi/eave-stdlib-ts/src/connect/lifecycle-router.js';
import { AtlassianProduct } from '@eave-fyi/eave-stdlib-ts/src/core-api/models/connect.js';
import express, { Request, Response, Router, Express, NextFunction } from 'express';
import eaveLogger, { LogContext } from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import appConfig from '../config.js';
import { JiraWebhookEvent } from '../types.js';
import commentCreatedEventHandler from './comment-created.js';
import JiraClient from '../jira-client.js';

export function applyWebhookMiddlewares({ app, addon, path }: {app: Express, addon: any, path: string}) {
  app.use(path, express.json());
  app.use(path, addon.middleware());
}

export function WebhookRouter({ addon }: { addon: any }): Router {
  // webhooks
  const router = Router();

  const lifecycleRouter = LifecycleRouter({ addon, product: AtlassianProduct.jira, eaveOrigin: appConfig.eaveOrigin });
  router.use(lifecycleRouter);

  router.post('/', addon.authenticate(), async (req: Request, res: Response, next: NextFunction) => {
    try {
      const ctx = LogContext.load(res);
      eaveLogger.info('received webhook event', ctx);
      const jiraClient = await JiraClient.getAuthedJiraClient({
        addon,
        clientKey: (<any>res.locals).clientKey, // TODO: make this typed
      });

      const payload = <JiraWebhookEvent>req.body;
      switch (payload.webhookEvent) {
        case 'comment_created':
          await commentCreatedEventHandler({ req, res, jiraClient });
          break;

        default:
          eaveLogger.warning(`unhandled webhook event: ${payload.webhookEvent}`, ctx);
          res.sendStatus(200);
      }

      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  return router;
}
