```shell
: '
This code file serves as a crucial configuration and routing module for handling webhooks in an Express.js application. It exports two main functions: `applyWebhookMiddlewares` and `WebhookRouter`.

The `applyWebhookMiddlewares` function is used to apply middleware to the Express application, specifically for parsing incoming raw JSON data from webhooks. This is a necessary step for accurate GitHub signature verification, ensuring the correct processing of this data.

The `WebhookRouter` function is responsible for creating and returning a new Express Router. This router is configured to handle incoming POST requests at the root ("/") of the application. Upon receiving a request, it uses the `dispatch` function to handle these requests and includes error handling logic, dispatching the request and response objects to a separate function for further processing.

Overall, the purpose of this file is to set up and manage the routing and data handling for incoming webhook events within the application, enabling the application to receive and correctly process these events.
'
```
Please note that Shell scripts do not have a specific syntax for multi-line comments. The above approach is a common workaround using a no-op command `:` and a multi-line string.


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
