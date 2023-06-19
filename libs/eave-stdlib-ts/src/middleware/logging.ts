import { Request, Response, NextFunction } from 'express';
import onFinished from 'on-finished';
import { getEaveState } from '../lib/request-state.js';
import eaveLogger from '../logging.js';

export function requestLoggingMiddleware(_req: Request, res: Response, next: NextFunction) {
  const eaveState = getEaveState(res);
  eaveLogger.info(
    `Eave Server Request Start: ${eaveState.request_id}: ${eaveState.request_method} ${eaveState.request_path}`,
    eaveState,
  );

  onFinished(res, () => {
    eaveLogger.info(
      `Eave Server Request End: ${eaveState.request_id}: ${eaveState.request_method} ${eaveState.request_path}`,
      eaveState,
    );
  });

  next();
}
