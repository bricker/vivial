import { Express, IRouter, raw } from 'express';
import helmet from 'helmet';
import { requestLoggingMiddleware } from './logging.js';
import { requestIntegrityMiddleware } from './request-integrity.js';
import { exceptionHandlingMiddleware } from './exception-handling.js';
import { requireHeaders } from './require-headers.js';
import { originMiddleware } from './origin.js';
import { signatureVerification } from './signature-verification.js';
import headers from '../headers.js';
import { jsonParser } from './body-parser.js';

// This isn't included in the common middlewares so individual apps can configure it as needed.
export const helmetMiddleware = helmet;

export const commonRequestMiddlewares = [
  requestIntegrityMiddleware,
  requestLoggingMiddleware,
];

// export function applyCommonRequestMiddlewares({ router }: { router: IRouter }) {
//   router.use(requestIntegrityMiddleware);
//   router.use(requestLoggingMiddleware);
// }

export const commonResponseMiddlewares = [
  exceptionHandlingMiddleware,
];

// export function applyCommonResponseMiddlewares({ router }: { router: IRouter }) {
//   router.use(exceptionHandlingMiddleware);
// }

export const rawJsonBody = raw({ type: 'application/json', limit: '5mb' });

export const commonInternalApiMiddlewares = [
  /*
  It's important that the body isn't parsed (eg with `express.json()`) before signature verification.
  For example, running the body through JSON.parse(), and then through JSON.stringify(), will yield different bytes
  than the original body, causing signature verification to fail.
  */
  rawJsonBody,
  requireHeaders(headers.EAVE_SIGNATURE_HEADER, headers.EAVE_TEAM_ID_HEADER, headers.EAVE_ORIGIN_HEADER),
  originMiddleware,
  signatureVerification(),
];

// export function applyInternalApiMiddlewares({ router }: { router: IRouter }) {
//   /*
//   Using raw parsing rather than express.json() parser because of GitHub signature verification.
//   If even 1 byte were different after passing through JSON.parse and then the signature verification would fail.
//   */
//   router.use(raw({ type: 'application/json', limit: '5mb' }));
//   router.use(requireHeaders(headers.EAVE_SIGNATURE_HEADER, headers.EAVE_TEAM_ID_HEADER, headers.EAVE_ORIGIN_HEADER));
//   router.use(originMiddleware);
//   router.use(signatureVerification());

//   // This goes _after_ signature verification, so that signature verification has access to the raw body.
//   router.use(bodyParser);
// }
