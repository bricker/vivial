import { Request, Response, NextFunction } from 'express';
import { getEaveState } from '../lib/request-state.js';
import eaveLogger from '../logging.js';

export function loggingMiddleware(req: Request, res: Response, next: NextFunction): void {
  const eaveState = getEaveState(res);
  eaveLogger.info({
    message: `Request Start: ${eaveState.request_id}: ${eaveState.request_method} ${eaveState.request_path}`,
    body: req.body,
    eaveState,
  });
  next();
}
