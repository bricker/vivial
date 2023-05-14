import { Request, Response, NextFunction } from 'express';
import { sharedConfig } from '../config.js';

// TODO: actual signing
export async function signatureVerification(req: Request, res: Response, next: NextFunction): Promise<void> {
  const eaveHeaderSecret = req.header('eave-signature');

  if (expectedEaveSecret === eaveHeaderSecret) {
    next();
  } else {
    res.statusMessage = 'Invalid Eave signature';
    res.status(401).end();
  }
}
