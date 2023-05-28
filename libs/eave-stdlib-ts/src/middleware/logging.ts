import { Request, Response, NextFunction } from 'express';
import { getEaveState } from '../lib/request-state';
import eaveLogger from '../logging';

export function loggingMiddleware(_: Request, res: Response, next: NextFunction): void {
  const eaveState = getEaveState(res);
  eaveLogger.info(`Request Start: ${eaveState.request_id}: ${eaveState.request_method} ${eaveState.request_path}`, eaveState);
  next();
}
