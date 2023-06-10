import { NextFunction, Request, RequestHandler, Response, Router, raw, Express } from 'express';
import { AddOn } from "atlassian-connect-express";
import getAvailableSpaces from './get-available-spaces.js';
import searchContent from './search-content.js';
import createContent from './create-content.js';
import updateContent from './update-content.js';
import deleteContent from './delete-content.js';


export function InternalApiRouter({addon}: {addon: AddOn}): Router {
  const router = Router();

  router.post('/spaces/query', async (req: Request, res: Response, next: NextFunction) => {
    try {
      await getAvailableSpaces(req, res, addon);
      next();
    } catch (e: unknown) {
      next(e);
    }
  });

  router.post('/content/search', async (req: Request, res: Response, next: NextFunction) => {
    try {
      await searchContent(req, res, addon);
      next();
    } catch (e: unknown) {
      next(e);
    }
  });

  router.post('/content/create', async (req: Request, res: Response, next: NextFunction) => {
    try {
      await createContent(req, res, addon);
      next();
    } catch (e: unknown) {
      next(e);
    }
  });

  router.post('/content/update', async (req: Request, res: Response, next: NextFunction) => {
    try {
      await updateContent(req, res, addon);
      next();
    } catch (e: unknown) {
      next(e);
    }
  });

  router.post('/content/delete', async (req: Request, res: Response, next: NextFunction) => {
    try {
      await deleteContent(req, res, addon);
      next();
    } catch (e: unknown) {
      next(e);
    }
  });

  // internalApiRouter.all('/proxy', async (/* req: Request, res: Response */) => {
  //   // TODO: Confluence API proxy?
  // });

  return router;
}
