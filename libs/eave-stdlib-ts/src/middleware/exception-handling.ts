import { NextFunction, Request, Response } from 'express';
import { getEaveState } from '../lib/request-state.js';
import eaveLogger from '../logging.js';

// This function has to accept 4 parameters for Express to consider it an error handler
// https://github.com/expressjs/express/blob/f540c3b0195393974d4875a410f4c00a07a2ab60/lib/router/layer.js#L65
export function exceptionHandlingMiddleware(err: any, _req: Request, res: Response, _next: NextFunction): void {
  const eaveState = getEaveState(res);
  eaveLogger.error({ message: err.stack, eaveState });
  res.sendStatus(500);
}
