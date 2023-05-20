import { Request, Response, NextFunction } from 'express';
import eaveHeaders from '../headers';
import { EaveRequestState, getEaveState } from '../lib/request-state';
import { developmentBypassAllowed } from './development-bypass';
import { buildMessageToSign } from '../lib/requests';
import { getKey, verifySignatureOrException } from '../signing';
import { HTTPException } from '../exceptions';
import eaveLogger from '../logging';

/**
 * Reads the body and headers and verifies the signature.
 * Note that this middleware necessarily blocks the request until the full body is received,
 * so that it can calculate the expected signature and compare it to the provided signature.
 */
export async function signatureVerification(req: Request, res: Response, next: NextFunction): Promise<void> {
  if (developmentBypassAllowed(req)) {
    eaveLogger.warn('Bypassing signature verification in dev environment');
    next();
  }

  const { body } = req;
  const eaveState = getEaveState(res);
  if (doSignatureVerification(req, res, body, eaveState)) {
    next();
  }
}

function doSignatureVerification(req: Request, res: Response, body: Buffer, eaveState: EaveRequestState): boolean {
  const signature = req.header(eaveHeaders.EAVE_SIGNATURE_HEADER);

  if (signature === undefined) {
    res.statusMessage = 'Missing Eave signature header';
    res.status(401).end();
    return false;
  }

  const teamId = req.header(eaveHeaders.EAVE_TEAM_ID_HEADER);
  const accountId = req.header(eaveHeaders.EAVE_ACCOUNT_ID_HEADER);
  const origin = eaveState.eave_origin!;

  const message = buildMessageToSign(
    req.method,
    `${req.protocol}://${req.headers.host}${req.originalUrl}`, // reconstruct full request url
    eaveState.request_id!,
    origin,
    body.toString('utf8'),
    teamId,
    accountId,
  );

  const signingKey = getKey(origin);

  try {
    verifySignatureOrException(signingKey, message, signature);
  } catch (error) {
    const eaveError = <HTTPException>error;
    res.statusMessage = error.message;
    res.status(eaveError.statusCode).end();
    return false;
  }
  return true;
}
