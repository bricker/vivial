import { Request, Response, NextFunction } from 'express';
import eaveLogger from '../logging.js';
import { getEaveState } from '../lib/request-state.js';
import { sharedConfig } from '../config.js';

// This function has to accept 4 parameters for Express to consider it an error handler
// https://github.com/expressjs/express/blob/f540c3b0195393974d4875a410f4c00a07a2ab60/lib/router/layer.js#L65
// but because we don't use all the parameters we have to trick typescript and tell eslint to stfu
// eslint-disable-next-line
export function exceptionHandlingMiddleware(err: any, _req: Request, res: Response, _next: NextFunction): void {
  const eaveState = getEaveState(res);
  eaveLogger.error(err, eaveState);
  res.status(500).end();
}
