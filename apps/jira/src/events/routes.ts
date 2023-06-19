import { LifecycleRouter } from '@eave-fyi/eave-stdlib-ts/src/connect/lifecycle-router.js';
import { AtlassianProduct } from '@eave-fyi/eave-stdlib-ts/src/core-api/models/connect.js';
import { AddOn } from 'atlassian-connect-express';
import express, { Request, Response, Router, Express, NextFunction } from 'express';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { getEaveState } from '@eave-fyi/eave-stdlib-ts/src/lib/request-state.js';
import appConfig from '../config.js';
import { JiraWebhookEvent } from '../types.js';
import commentCreatedEventHandler from './comment-created.js';
import JiraClient from '../jira-client.js';

export function applyWebhookMiddlewares({ app, addon, path }: {app: Express, addon: AddOn, path: string}) {
  app.use(path, express.json());
  app.use(path, addon.middleware());
}

export function WebhookRouter({ addon }: { addon: AddOn }): Router {
  // webhooks
  const router = Router();

  const lifecycleRouter = LifecycleRouter({ addon, product: AtlassianProduct.jira, eaveOrigin: appConfig.eaveOrigin });
  router.use(lifecycleRouter);

  router.post('/', addon.authenticate(), async (req: Request, res: Response, next: NextFunction) => {
    try {
      const eaveState = getEaveState(res);
      eaveLogger.info({ message: 'received webhook event', eaveState });
      const jiraClient = await JiraClient.getAuthedJiraClient({
        req,
        addon,
        clientKey: (<any>res.locals).clientKey, // TODO: make this typed
      });

      const payload = <JiraWebhookEvent>req.body;
      switch (payload.webhookEvent) {
        case 'comment_created':
          await commentCreatedEventHandler({ req, res, jiraClient });
          break;

        default:
          eaveLogger.warn({ message: `unhandled webhook event: ${payload.webhookEvent}`, eaveState });
          res.sendStatus(200);
      }

      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  return router;
}
