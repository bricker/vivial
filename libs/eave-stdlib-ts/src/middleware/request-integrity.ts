import { Request, Response, NextFunction } from 'express';
import { EaveRequestState } from '../lib/request-state.js';
import eaveHeaders from '../headers.js';
import uuid from 'uuid';

/**
 * Makes sure the eaveState is set on `req.extensions.SCOPE` for signature verification. 
 */
export function requestIntegrity(req: Request, _: Response, next: NextFunction): void {
  const eaveState: EaveRequestState = {};

  const reqIdHeaderValue = req.header(eaveHeaders.EAVE_REQUEST_ID_HEADER);
  eaveState.request_id = reqIdHeaderValue === undefined ? uuid.v4() : reqIdHeaderValue;
  eaveState.request_method = req.method;
  eaveState.request_scheme = req.protocol;
  eaveState.request_path = req.path;

  eaveState.request_headers = {};
  const redactedHeaders = [eaveHeaders.EAVE_AUTHORIZATION_HEADER, eaveHeaders.EAVE_COOKIE_HEADER];
  Object.keys(req.headers).forEach(headerName => {
    if (redactedHeaders.includes(headerName)) {
      eaveState.request_headers![headerName] = '[redacted]';
    } else {
      eaveState.request_headers![headerName] = req.header(headerName)!;
    }
  });

  console.log(`Request: ${req.path}`);
  next();
}