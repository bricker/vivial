import { NextFunction, Request, Response, Router, raw, Express } from 'express';
import dispatch from '../dispatch.js';

/**
 * The `applyWebhookMiddlewares` function is designed to apply raw parsing middleware 
 * to a specified path in an Express application. This is necessary for the accurate 
 * verification of GitHub signatures, as using the express.json() parser could potentially 
 * alter the data and cause the verification to fail. The function sets a limit of 5mb 
 * for the parsed data.
 */
export function applyWebhookMiddlewares({ app, path }:{ app: Express, path: string }) {
  /*
  Using raw parsing rather than express.json() parser because of GitHub signature verification.
  If even 1 byte were different after passing through JSON.parse and then the signature verification would fail.
  */
  app.use(path, raw({ type: 'application/json', limit: '5mb' }));
}

/**
 * The `WebhookRouter` function is designed to handle HTTP POST requests made to the root URL ('/') of the server.
 * It uses an asynchronous function to dispatch the request and response objects, ensuring the request is processed 
 * and the response is sent back to the client. If any error occurs during this process, it is caught and passed 
 * to the next middleware function for error handling.
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
