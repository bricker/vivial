import { Request, Response, NextFunction } from 'express';
import { v4 as uuid4 } from 'uuid';
import { EaveRequestState, setEaveScope } from '../lib/request-state';
import eaveHeaders from '../headers';
import { EaveOrigin } from '../eave-origins';
import { BadRequestError } from '../exceptions';
import eaveLogger from '../logging';

/**
 * Makes sure the eaveState is set on `req.extensions.SCOPE` for signature verification.
 */
export function requestIntegrity(req: Request, res: Response, next: NextFunction): void {
  const eaveState: EaveRequestState = {};

  const reqIdHeaderValue = req.header(eaveHeaders.EAVE_REQUEST_ID_HEADER);
  eaveState.request_id = reqIdHeaderValue === undefined ? uuid4() : reqIdHeaderValue;
  eaveState.request_method = req.method;
  eaveState.request_scheme = req.protocol;
  eaveState.request_path = req.path;

  const originHeader = req.header(eaveHeaders.EAVE_ORIGIN_HEADER);
  if (originHeader === undefined) {
    // TODO: use res and return??
    throw new BadRequestError('Eave Origin header must be set');
  }
  const originValue = EaveOrigin[originHeader as keyof typeof EaveOrigin];
  if (originValue === undefined) {
    throw new BadRequestError(`Unexpected Eave Origin ${originHeader} could not be found`);
  }
  eaveState.eave_origin = originValue;

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
  setEaveScope(res, eaveState);

  eaveLogger.info(`Request: ${req.path}`, eaveState);
  next();
}
