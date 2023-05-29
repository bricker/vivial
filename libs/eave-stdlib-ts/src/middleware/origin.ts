import { Request, Response, NextFunction } from 'express';
import { getEaveState, setEaveState } from '../lib/request-state.js';
import eaveHeaders from '../headers.js';
import { EaveOrigin } from '../eave-origins.js';
import eaveLogger from '../logging.js';

export function originMiddleware(req: Request, res: Response, next: NextFunction): void {
  const eaveState = getEaveState(res);
  const originHeader = req.header(eaveHeaders.EAVE_ORIGIN_HEADER);

  if (originHeader === undefined) {
    eaveLogger.warning('missing origin header', eaveState);
    res.status(400).end();
    return;
  }

  const originValue = EaveOrigin[originHeader as keyof typeof EaveOrigin];
  if (originValue === undefined) {
    eaveLogger.warning(`invalid origin header ${originHeader}`, eaveState);
    res.status(400).end();
    return;
  }
  eaveState.eave_origin = originValue;

  setEaveState(res, eaveState);
  next();
}
