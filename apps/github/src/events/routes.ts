/**
 * This code file is primarily designed to manage and set up webhooks in an Express.js application.
 * It exports two main functions: applyWebhookMiddlewares and WebhookRouter.
 * 
 * The applyWebhookMiddlewares function is used to apply middleware to the application, specifically for handling raw JSON data.
 * This is crucial for correctly processing GitHub's signature verification system and ensuring data integrity.
 * 
 * The WebhookRouter function, on the other hand, creates and returns a new Express Router that is configured to handle POST requests at its root path.
 * Upon receiving a request, it dispatches the request and response objects to a separate function for further processing.
 * 
 * The main purpose of this file is to receive, process, and route incoming webhook requests to the appropriate handlers within the application,
 * making it a vital component for the application's ability to correctly process incoming webhook events.
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
