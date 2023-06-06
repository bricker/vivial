import { Request, Response, NextFunction } from 'express';
import eaveHeaders from '../headers.js';
import { getEaveState } from '../lib/request-state.js';
import { developmentBypassAllowed } from './development-bypass.js';
import { buildMessageToSign } from '../lib/requests.js';
import { getKey, verifySignatureOrException } from '../signing.js';
import { HTTPException } from '../exceptions.js';
import eaveLogger from '../logging.js';

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

  let serializedBody;
  if (typeof body === 'string' || body instanceof Buffer) {
    serializedBody = body.toString();
  } else {
    serializedBody = JSON.stringify(body);
  }

  const message = buildMessageToSign({
    method: req.method,
    url: `${baseUrl}${req.originalUrl}`,
    requestId: eaveState.request_id!,
    origin,
    payload: serializedBody,
    teamId,
    accountId,
  });

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
