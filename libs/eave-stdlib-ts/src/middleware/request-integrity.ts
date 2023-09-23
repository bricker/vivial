import { Request, Response, NextFunction } from 'express';
import { LogContext } from '../logging.js';
import { EAVE_CTX_KEY } from '../headers.js';

export function requestIntegrityMiddleware(_req: Request, res: Response, next: NextFunction): void {
  const ctx = LogContext.load(res);
  res.locals[EAVE_CTX_KEY] = ctx;
  next();
}
