import { Request, Response, NextFunction } from 'express';

export function requestIntegrityMiddleware(req: Request, res: Response, next: NextFunction): void {
  // This is here for parity with Python but doesn't do anything in express
  next();
}
