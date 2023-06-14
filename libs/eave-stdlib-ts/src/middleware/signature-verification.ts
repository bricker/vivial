import { Request, Response, NextFunction } from 'express';
import eaveHeaders from '../headers.js';
import { getEaveState } from '../lib/request-state.js';
import { developmentBypassAllowed } from './development-bypass.js';
import { buildMessageToSign } from '../lib/requests.js';
import Signing from '../signing.js';
import eaveLogger from '../logging.js';

/**
 * Reads the body and headers and verifies the signature.
 * Note that this middleware necessarily blocks the request until the full body is received,
 * so that it can calculate the expected signature and compare it to the provided signature.
 */
export function signatureVerification(baseUrl: string): ((req: Request, res: Response, next: NextFunction) => void) {
  return async (req: Request, res: Response, next: NextFunction) => {
    const eaveState = getEaveState(res);
    try {
      await doSignatureVerification(req, res, baseUrl);
      next();
    } catch (e: any) {
      if (developmentBypassAllowed(req)) {
        eaveLogger.warning({ message: 'Bypassing signature verification in dev environment', eaveState });
        next();
      } else {
        next(e);
      }
    }
  };
}

async function doSignatureVerification(req: Request, res: Response, baseUrl: string): Promise<boolean> {
  const eaveState = getEaveState(res);
  const signature = req.header(eaveHeaders.EAVE_SIGNATURE_HEADER);

  if (signature === undefined) {
    eaveLogger.warning({ message: 'Missing Eave signature header', eaveState });
    res.sendStatus(400);
    return false;
  }

  const teamId = req.header(eaveHeaders.EAVE_TEAM_ID_HEADER);
  const accountId = req.header(eaveHeaders.EAVE_ACCOUNT_ID_HEADER);
  const origin = eaveState.eave_origin!;

  // let serializedBody;
  // if (typeof req.body === 'string' || req.body instanceof Buffer) {
  //   serializedBody = req.body.toString();
  // } else {
  //   serializedBody = JSON.stringify(req.body, undefined, 0);
  // }

  const payload = (<Buffer>req.body).toString();

  const message = buildMessageToSign({
    method: req.method,
    url: `${baseUrl}${req.originalUrl}`,
    requestId: eaveState.request_id!,
    origin,
    payload,
    teamId,
    accountId,
  });

  const signing = Signing.new(origin);
  await signing.verifySignatureOrException(message, signature);
  return true;
}
