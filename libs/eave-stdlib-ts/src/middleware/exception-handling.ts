import { NextFunction, Request, Response } from 'express';
import { eaveLogger, LogContext } from '../logging.js';

// This function has to accept 4 parameters for Express to consider it an error handler
// https://github.com/expressjs/express/blob/f540c3b0195393974d4875a410f4c00a07a2ab60/lib/router/layer.js#L65
export function exceptionHandlingMiddleware(err: any, _req: Request, res: Response, _next: NextFunction): void {
  const ctx = LogContext.load(res);
  eaveLogger.error(err, ctx);
  res.sendStatus(500);
}
