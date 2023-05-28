import { Request, Response, NextFunction } from 'express';
import eaveHeaders from '../headers';
import { getEaveState } from '../lib/request-state';
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
export function signatureVerification(baseUrl: string): ((req: Request, res: Response, next: NextFunction) => void) {
  return (req: Request, res: Response, next: NextFunction) => {
    if (developmentBypassAllowed(req)) {
      eaveLogger.warning('Bypassing signature verification in dev environment');
      next();
      return;
    }

    const { body } = req;
    if (doSignatureVerification(req, res, body, baseUrl)) {
      next();
    } else {
      const eaveState = getEaveState(res);
      eaveLogger.warning('signature validation failed', eaveState);
      res.status(400).end();
      return;
    }
  };
}

function doSignatureVerification(req: Request, res: Response, body: Buffer, baseUrl: string): boolean {
  const eaveState = getEaveState(res);
  const signature = req.header(eaveHeaders.EAVE_SIGNATURE_HEADER);

  if (signature === undefined) {
    eaveLogger.warning('Missing Eave signature header', eaveState);
    res.status(400).end();
    return false;
  }

  const teamId = req.header(eaveHeaders.EAVE_TEAM_ID_HEADER);
  const accountId = req.header(eaveHeaders.EAVE_ACCOUNT_ID_HEADER);
  const origin = eaveState.eave_origin!;

  const message = buildMessageToSign(
    req.method,
    `${baseUrl}${req.originalUrl}`,
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
    eaveLogger.error(eaveError);
    res.status(eaveError.statusCode).end();
    return false;
  }
  return true;
}
