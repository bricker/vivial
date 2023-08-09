import { NextFunction, Request, Response, Router } from 'express';
import { inlineCodeDocs } from './inline-code-docs.js';

export function InternalApiRouter(): Router {
  const router = Router();

  router.post('/events', async (req: Request, res: Response, next: NextFunction) => {
    try {
      await inlineCodeDocs(req, res);
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  return router;
}
