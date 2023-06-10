import { Express, NextFunction, Request, RequestHandler, Response, raw } from 'express';
import helmet from 'helmet';
import { requestIntegrity } from './request-integrity.js';
import { requestLoggingMiddleware, responseLoggingMiddleware } from './logging.js';
import { exceptionHandlingMiddleware } from './exception-handling.js';
import { requireHeaders } from './require-headers.js';
import { originMiddleware } from './origin.js';
import { signatureVerification } from './signature-verification.js';
import headers from '../headers.js';
import { sharedConfig } from '../config.js';
import { bodyParser } from './body-parser.js';

// This isn't included in the common middlewares so individual apps can configure it as needed.
export const helmetMiddleware = helmet;

export function applyCommonRequestMiddlewares({ app }: { app: Express }) {
  app.use(requestIntegrity);
  app.use(requestLoggingMiddleware);
}

export function applyCommonResponseMiddlewares({ app }: { app: Express }) {
  app.use(responseLoggingMiddleware);
  app.use(exceptionHandlingMiddleware);
  }

export function applyInternalApiMiddlewares({ app, path }: {app: Express, path: string}) {
  /*
  Using raw parsing rather than express.json() parser because of GitHub signature verification.
  If even 1 byte were different after passing through JSON.parse and then the signature verification would fail.
  */
  app.use(path, raw({ type: 'application/json' }));
  app.use(path, requireHeaders(headers.EAVE_SIGNATURE_HEADER, headers.EAVE_TEAM_ID_HEADER, headers.EAVE_ORIGIN_HEADER));
  app.use(path, originMiddleware);
  app.use(path, signatureVerification(sharedConfig.eaveAppsBase));

  // This goes _after_ signature verification, so that signature verification has access to the raw body.
  app.use(path, bodyParser);
}