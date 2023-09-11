import { AddOn } from 'atlassian-connect-express';
import { Request, Response, Router, NextFunction } from 'express';
import { LifecycleRouter } from '@eave-fyi/eave-stdlib-ts/src/connect/lifecycle-router.js';
import { AtlassianProduct } from '@eave-fyi/eave-stdlib-ts/src/core-api/models/connect.js';
import eaveLogger, { LogContext } from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { jsonParser } from '@eave-fyi/eave-stdlib-ts/src/middleware/body-parser.js';
import appConfig from '../config.js';
import { JiraWebhookEvent } from '../types.js';
import commentCreatedEventHandler from './comment-created.js';
import JiraClient from '../jira-client.js';

export function WebhookRouter({ addon }: { addon: AddOn }): Router {
  // webhooks
  const router = Router();
  router.use(jsonParser);
  router.use(addon.middleware());

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
