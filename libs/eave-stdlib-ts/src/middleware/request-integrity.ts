import { Request, Response, NextFunction } from 'express';
import headers from '../headers.js';
import { LogContext } from '../logging.js';

export function requestIntegrityMiddleware(_req: Request, res: Response, next: NextFunction): void {
  const ctx = LogContext.load(res);
  res.locals[headers.EAVE_CTX_KEY] = ctx;
  next();
}
