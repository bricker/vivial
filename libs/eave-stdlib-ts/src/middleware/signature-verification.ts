import { Request, Response, NextFunction } from 'express';
import { sharedConfig } from '../config.js';

/**
 * Reads the body and headers and verifies the signature.
 * Note that this middleware necessarily blocks the request until the full body is received,
 * so that it can calculate the expected signature and compare it to the provided signature.
 */
export async function signatureVerification(req: Request, res: Response, next: NextFunction): Promise<void> {
  const eaveHeaderSecret = req.header('eave-signature');

  if (expectedEaveSecret === eaveHeaderSecret) {
    next();
  } else {
    res.statusMessage = 'Invalid Eave signature';
    res.status(401).end();
  }
}
