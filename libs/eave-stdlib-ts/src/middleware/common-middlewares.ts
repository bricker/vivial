import { raw } from 'express';
import helmet from 'helmet';
import { requestLoggingMiddleware } from './logging.js';
import { requestIntegrityMiddleware } from './request-integrity.js';
import { exceptionHandlingMiddleware } from './exception-handling.js';
import { requireHeaders } from './require-headers.js';
import { originMiddleware } from './origin.js';
import { signatureVerification } from './signature-verification.js';
import headers from '../headers.js';

// This isn't included in the common middlewares so individual apps can configure it as needed.
export const helmetMiddleware = helmet;

export const commonRequestMiddlewares = [
  requestIntegrityMiddleware,
  requestLoggingMiddleware,
];

export const commonResponseMiddlewares = [
  exceptionHandlingMiddleware,
];

export const rawJsonBody = raw({ type: 'application/json', limit: '5mb' });

export const commonInternalApiMiddlewares = [
  /*
  It's important that the body isn't parsed (eg with `express.json()`) before signature verification. For example, running the body through JSON.parse(), and then through JSON.stringify(), will yield different bytes than the original body (probably differences in spacing/indentation), causing signature verification to fail.
  Apps should apply their own body parsers (ideally using the `body-parser` middleware).
  */
  rawJsonBody,
  requireHeaders(headers.EAVE_SIGNATURE_HEADER, headers.EAVE_TEAM_ID_HEADER, headers.EAVE_ORIGIN_HEADER),
  originMiddleware,
  signatureVerification(),
];
