import { Request, Response, NextFunction } from 'express';
import { v4 as uuid4 } from 'uuid';
import onFinished from 'on-finished';
import { EaveRequestState, getEaveState, setEaveState } from '../lib/request-state.js';
import eaveLogger from '../logging.js';
import headers from '../headers.js';

export function requestLoggingMiddleware(req: Request, res: Response, next: NextFunction) {
  const eaveState = getEaveState(res);
  eaveLogger.info({
    message: `Eave Server Request Start: ${eaveState.request_id}: ${eaveState.request_method} ${eaveState.request_path}`,
    eaveState,
  });

  onFinished(res, () => {
    eaveLogger.info({
      message: `Eave Server Request End: ${eaveState.request_id}: ${eaveState.request_method} ${eaveState.request_path}`,
      eaveState,
    });
  });

  next();
}
