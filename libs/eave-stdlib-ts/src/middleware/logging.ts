import { Request, Response, NextFunction } from 'express';
import { getEaveState } from '../lib/request-state.js';
import eaveLogger from '../logging.js';

export function requestLoggingMiddleware(req: Request, res: Response, next: NextFunction) {
  const eaveState = getEaveState(res);
  eaveLogger.info({
    message: `Eave Server Request Start: ${eaveState.request_id}: ${eaveState.request_method} ${eaveState.request_path}`,
    eaveState,
  });
  next();
}

export async function responseLoggingMiddleware(_: Request, res: Response, next: NextFunction) {
  const eaveState = getEaveState(res);

  eaveLogger.info({
    message: `Eave Server Request End: ${eaveState.request_id}: ${eaveState.request_method} ${eaveState.request_path}`,
    eaveState,
  });

  next();
}
