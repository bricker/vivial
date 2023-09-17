import { NextFunction, Request, Response, Router } from 'express';
import { commonInternalApiMiddlewares } from '@eave-fyi/eave-stdlib-ts/src/middleware/common-middlewares.js';
import { jsonParser } from '@eave-fyi/eave-stdlib-ts/src/middleware/body-parser.js';
import { getSummary } from './content.js';
import { subscribe } from './subscribe.js';
import { createPullRequest } from './create-pull-request.js';

export function InternalApiRouter(): Router {
  const router = Router();
  router.use(...commonInternalApiMiddlewares);
  router.use(jsonParser);

  router.post('/api/content', async (req: Request, res: Response, next: NextFunction) => {
    try {
      await getSummary(req, res);
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  router.post('/api/subscribe', async (req: Request, res: Response, next: NextFunction) => {
    try {
      await subscribe(req, res);
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  router.post('/create-pull-request', async (req: Request, res: Response, next: NextFunction) => {
    try {
      await createPullRequest(req, res);
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  return router;
}
