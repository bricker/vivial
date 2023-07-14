import { NextFunction, Request, Response, Router } from 'express';
import someEndpoint from './some-endpoint.js';

export function InternalApiRouter(): Router {
  const router = Router();

  router.post('/some/endpoint', async (req: Request, res: Response, next: NextFunction) => {
    try {
      await someEndpoint({ req, res });
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  return router;
}
