import { NextFunction, Request, Response, Router } from "express";
import { getSummary } from "./content.js";
import { subscribe } from "./subscribe.js";

export function InternalApiRouter(): Router {
  const router = Router();

  router.post('/content', async (req: Request, res: Response, next: NextFunction) => {
    try {
      await getSummary(req, res);
      next();
    } catch (e: unknown) {
      next(e);
    }
  });

  router.post('/subscribe', async (req: Request, res: Response, next: NextFunction) => {
    try {
      await subscribe(req, res);
      next();
    } catch (e: unknown) {
      next(e);
    }
  });

  return router;
}
