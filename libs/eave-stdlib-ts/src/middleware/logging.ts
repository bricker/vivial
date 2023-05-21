import { Request, Response, NextFunction } from 'express';
import { getEaveState } from '../lib/request-state.js';
import eaveLogger from '../logging.js';

export function loggingMiddleware(_: Request, res: Response, next: NextFunction): void {
  const eaveState = getEaveState(res);
  eaveLogger.info(`Request Start: ${eaveState.request_id}: ${eaveState.request_method} ${eaveState.request_path}`, eaveState);

  next();

  eaveLogger.info(`Request End: ${eaveState.request_id}: ${eaveState.request_method} ${eaveState.request_path}`, eaveState);
}
