import { NextFunction, Request, Response, Router, raw, Express } from 'express';
import dispatch from '../dispatch.js';

/**
 * This function applies raw parsing middleware to a specified path on an Express application.
 * 
 * The raw parsing is used instead of express.json() parser due to the necessity of GitHub signature verification.
 * If even a single byte were different after passing through JSON.parse, the signature verification would fail.
 * 
 * @param {Object} {app, path} - An object containing the Express application and the path to apply the middleware to.
 * @param {Express} {app, path}.app - The Express application.
 * @param {string} {app, path}.path - The path on the Express application to apply the middleware to.
 * 
 * @example
 * applyWebhookMiddlewares({ app: expressApp, path: '/webhook' });
 */
export function applyWebhookMiddlewares({ app, path }:{ app: Express, path: string }) {
  /*
  Using raw parsing rather than express.json() parser because of GitHub signature verification.
  If even 1 byte were different after passing through JSON.parse and then the signature verification would fail.
  */
  app.use(path, raw({ type: 'application/json', limit: '5mb' }));
}

/**
       * This function creates and returns a new Express Router instance for handling webhook requests.
       * It sets up a POST route at the root path ('/') of the router.
       * When a POST request is received, it attempts to dispatch the request and send a response.
       * If an error occurs during this process, it passes the error to the next middleware function in the stack.
       *
       * @returns {Router} An Express Router instance configured to handle webhook requests.
       */
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
