import { Request, Response, NextFunction } from 'express';
import { EaveApp } from '../eave-origins.js';
import { eaveLogger, LogContext } from '../logging.js';
import { EAVE_ORIGIN_HEADER } from '../headers.js';

export function originMiddleware(req: Request, res: Response, next: NextFunction): void {
  const ctx = LogContext.load(res);
  const originHeader = req.header(EAVE_ORIGIN_HEADER);

  if (originHeader === undefined) {
    eaveLogger.warning('missing origin header', ctx);
    res.sendStatus(400);
    return;
  }

  const originValue = EaveApp[originHeader as keyof typeof EaveApp];
  if (originValue === undefined) {
    eaveLogger.warning(`invalid origin header ${originHeader}`, ctx);
    res.sendStatus(400);
    return;
  }
  ctx.eave_origin = originValue;
  next();
}
