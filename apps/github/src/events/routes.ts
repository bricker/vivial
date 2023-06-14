import { NextFunction, Request, Response, Router, raw, Express } from 'express';
import dispatch from '../dispatch.js';

export function applyWebhookMiddlewares({ app, path }:{ app: Express, path: string }) {
  /*
  Using raw parsing rather than express.json() parser because of GitHub signature verification.
  If even 1 byte were different after passing through JSON.parse and then the signature verification would fail.
  */
  app.use(path, raw({ type: 'application/json' }));
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
