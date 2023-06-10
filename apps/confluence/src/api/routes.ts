import { NextFunction, Request, RequestHandler, Response, Router, raw } from 'express';
import { AddOn } from "atlassian-connect-express";
import { requireHeaders } from '@eave-fyi/eave-stdlib-ts/src/middleware/require-headers.js';
import headers from '@eave-fyi/eave-stdlib-ts/src/headers.js';
import { originMiddleware } from '@eave-fyi/eave-stdlib-ts/src/middleware/origin.js';
import { signatureVerification } from '@eave-fyi/eave-stdlib-ts/src/middleware/signature-verification.js';
import { bodyParser } from '@eave-fyi/eave-stdlib-ts/src/middleware/body-parser.js';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import getAvailableSpaces from './get-available-spaces.js';
import searchContent from './search-content.js';
import createContent from './create-content.js';
import updateContent from './update-content.js';
import appConfig from '../config.js';
import deleteContent from './delete-content.js';

export function internalApiMiddlewares(): RequestHandler[] {
  return [
    raw({ type: 'application/json' }),
    requireHeaders(headers.EAVE_SIGNATURE_HEADER, headers.EAVE_TEAM_ID_HEADER, headers.EAVE_ORIGIN_HEADER),
    originMiddleware,
    signatureVerification(appConfig.eaveAppsBase),
    bodyParser, // This goes _after_ signature verification, so that signature verification has access to the raw body.
  ];
}

export function InternalApiRouter({ addon }: { addon: AddOn }): Router {
  const internalApiRouter = Router();

  internalApiRouter.post('/spaces/query', async (req: Request, res: Response, next: NextFunction) => {
    try {
      await getAvailableSpaces(req, res, addon);
      next();
    } catch (e: unknown) {
      next(e);
    }
  });

  internalApiRouter.post('/content/search', async (req: Request, res: Response, next: NextFunction) => {
    try {
      await searchContent(req, res, addon);
      next();
    } catch (e: unknown) {
      next(e);
    }
  });

  internalApiRouter.post('/content/create', async (req: Request, res: Response, next: NextFunction) => {
    try {
      await createContent(req, res, addon);
      next();
    } catch (e: unknown) {
      next(e);
    }
  });

  internalApiRouter.post('/content/update', async (req: Request, res: Response, next: NextFunction) => {
    try {
      await updateContent(req, res, addon);
      next();
    } catch (e: unknown) {
      next(e);
    }
  });

  internalApiRouter.post('/content/delete', async (req: Request, res: Response, next: NextFunction) => {
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

  return internalApiRouter;
}
