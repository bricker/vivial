import { Request, Response, NextFunction } from 'express';
import { getEaveState, setEaveState } from '../lib/request-state.js';
import eaveHeaders from '../headers.js';
import { EaveOrigin } from '../eave-origins.js';
import eaveLogger from '../logging.js';

export function originMiddleware(req: Request, res: Response, next: NextFunction): void {
  const eaveState = getEaveState(res);
  const originHeader = req.header(eaveHeaders.EAVE_ORIGIN_HEADER);

  if (originHeader === undefined) {
    eaveLogger.warn({ message: 'missing origin header', eaveState });
    res.sendStatus(400);
    return;
  }

  const originValue = EaveOrigin[originHeader as keyof typeof EaveOrigin];
  if (originValue === undefined) {
    eaveLogger.warn({ message: `invalid origin header ${originHeader}`, eaveState });
    res.sendStatus(400);
    return;
  }
  eaveState.eave_origin = originValue;

  setEaveState(res, eaveState);
  next();
}
