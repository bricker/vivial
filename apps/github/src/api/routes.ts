import { NextFunction, Request, Response, Router } from 'express';
import { commonInternalApiMiddlewares } from '@eave-fyi/eave-stdlib-ts/src/middleware/common-middlewares.js';
import { jsonParser } from '@eave-fyi/eave-stdlib-ts/src/middleware/body-parser.js';
import { getSummary } from './content.js';
import { subscribe } from './subscribe.js';

export function InternalApiRouter(): Router {
  const router = Router();
  router.use(commonInternalApiMiddlewares, jsonParser);

  router.post('/content', async (req: Request, res: Response, next: NextFunction) => {
    try {
      await getSummary(req, res);
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  router.post('/subscribe', async (req: Request, res: Response, next: NextFunction) => {
    try {
      await subscribe(req, res);
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  return router;
}
