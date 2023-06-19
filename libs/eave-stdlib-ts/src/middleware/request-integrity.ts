import { Request, Response, NextFunction } from 'express';
import { v4 as uuid4 } from 'uuid';
import { EaveRequestState, setEaveState } from '../lib/request-state.js';
import eaveHeaders from '../headers.js';

/**
 * Makes sure the eaveState is set on `req.extensions.SCOPE` for signature verification.
 */
export function requestIntegrityMiddleware(req: Request, res: Response, next: NextFunction): void {
  const eaveState: EaveRequestState = {};

  const reqIdHeaderValue = req.header(eaveHeaders.EAVE_REQUEST_ID_HEADER);
  eaveState.request_id = reqIdHeaderValue === undefined ? uuid4() : reqIdHeaderValue;
  eaveState.request_method = req.method;
  eaveState.request_scheme = req.protocol;
  // the 'path' property chops off the mount prefix, eg /github/api/content -> /content. originalUrl gives the full path.
  eaveState.request_path = req.originalUrl;

  eaveState.request_headers = {};
  const redactedHeaders = [eaveHeaders.EAVE_AUTHORIZATION_HEADER, eaveHeaders.EAVE_COOKIE_HEADER];
  Object.keys(req.headers).forEach((headerName) => {
    if (redactedHeaders.includes(headerName)) {
      eaveState.request_headers![headerName] = '[redacted]';
    } else {
      eaveState.request_headers![headerName] = req.header(headerName)!;
    }
  });

  // save constructed eaveState for future middlewares
  setEaveState(res, eaveState);
  next();
}
