import { raw } from 'express';
import helmet from 'helmet';
import { requestLoggingMiddleware } from './logging.js';
import { requestIntegrityMiddleware } from './request-integrity.js';
import { exceptionHandlingMiddleware } from './exception-handling.js';

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
