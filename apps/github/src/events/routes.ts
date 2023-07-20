###
/**
* This code file is designed to manage webhooks within an Express application. It is primarily responsible for 
* setting up and handling the middleware for processing raw JSON data, which is crucial for the correct 
* processing of GitHub signature verifications. The file also sets up a router to handle POST requests, 
* dispatching these requests for further processing. The overall purpose of this file is to enable the 
* application to receive and correctly process incoming webhook events.
*/
###

/**
* This code file is primarily responsible for setting up and managing webhooks in an Express application.
* It exports two main functions: applyWebhookMiddlewares and WebhookRouter.
*
* The applyWebhookMiddlewares function is used to apply middleware to the Express application, specifically
* for handling raw JSON data. This is necessary for correctly processing GitHub signature verifications.
*
* The WebhookRouter function creates and returns a new Express Router. This router is configured to handle
* POST requests at its root path. Upon receiving a request, it dispatches the request and response objects
* to a separate function for further processing.
*
* Overall, this file is crucial for enabling the application to receive and correctly process incoming webhook events.
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