/**
 * This code file primarily serves to set up and manage webhooks for an application using the Express.js framework. 
 * It includes functions to apply middleware for handling webhook requests and to create a router for processing 
 * POST requests to the webhook. The file ensures that incoming webhook data is correctly parsed and dispatched, 
 * while also providing error handling capabilities.
 */

import { NextFunction, Request, Response, Router, raw, Express } from 'express';
import dispatch from '../dispatch.js';

export function applyWebhookMiddlewares({ app, path }:{ app: Express, path: string }) {
  /*
  Using raw parsing rather than express.json() parser because of GitHub signature verification.
  If even 1 byte were different after passing through JSON.parse and then the signature verification would fail.
  */
  app.use(path, raw({ type: 'application/json', limit: '5mb' }));
}

export function WebhookRouter(): Router {
  const router = Router();

  router.post('/', async (req: Request, res: Response, next: NextFunction) => {
    try {
      await dispatch(req, res);
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  return router;
}
