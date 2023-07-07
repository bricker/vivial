import { Request, Response, NextFunction } from 'express';
import eaveHeaders from '../headers.js';
import { developmentBypassAllowed } from './development-bypass.js';
import Signing, { buildMessageToSign } from '../signing.js';
import eaveLogger, { LogContext } from '../logging.js';

/**
 * Reads the body and headers and verifies the signature.
 * Note that this middleware necessarily blocks the request until the full body is received,
 * so that it can calculate the expected signature and compare it to the provided signature.
 */
export function signatureVerification(): ((req: Request, res: Response, next: NextFunction) => void) {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      await doSignatureVerification(req, res);
      next();
    } catch (e: any) {
      if (developmentBypassAllowed(req, res)) {
        next();
      } else {
        next(e);
      }
    }
  };
}

async function doSignatureVerification(req: Request, res: Response): Promise<boolean> {
  const ctx = LogContext.load(res);
  const signature = req.header(eaveHeaders.EAVE_SIGNATURE_HEADER);

  if (signature === undefined) {
    eaveLogger.error('Missing Eave signature header', ctx);
    res.sendStatus(400);
    return false;
  }

  const teamId = req.header(eaveHeaders.EAVE_TEAM_ID_HEADER);
  const accountId = req.header(eaveHeaders.EAVE_ACCOUNT_ID_HEADER);
  const origin = ctx.eave_origin!;
  const audience = req.header(eaveHeaders.HOST);

  // let serializedBody;
  // if (typeof req.body === 'string' || req.body instanceof Buffer) {
  //   serializedBody = req.body.toString();
  // } else {
  //   serializedBody = JSON.stringify(req.body, undefined, 0);
  // }

  const payload = (<Buffer>req.body).toString();

  const message = buildMessageToSign({
    method: req.method,
    url: `${audience}${req.originalUrl}`,
    requestId: ctx.eave_request_id,
    origin,
    payload,
    teamId,
    accountId,
  });

  const signing = Signing.new(origin);
  await signing.verifySignatureOrException(message, signature);
  return true;
}
