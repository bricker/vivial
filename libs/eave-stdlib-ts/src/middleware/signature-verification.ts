import { NextFunction, Request, Response } from "express";
import { EaveApp } from "../eave-origins.js";
import * as eaveHeaders from "../headers.js";
import { LogContext } from "../logging.js";
import Signing, { buildMessageToSign, makeSigTs } from "../signing.js";
import { developmentBypassAllowed } from "./development-bypass.js";

const MAX_SIGNATURE_AGE = 60 * 60; // 1h

/**
 * Reads the body and headers and verifies the signature.
 * Note that this middleware necessarily blocks the request until the full body is received,
 * so that it can calculate the expected signature and compare it to the provided signature.
 */
export function signatureVerification({
  audience,
}: {
  audience: EaveApp;
}): (req: Request, res: Response, next: NextFunction) => void {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      await doSignatureVerification(req, res, audience);
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

async function doSignatureVerification(
  req: Request,
  res: Response,
  audience: EaveApp,
): Promise<void> {
  const ctx = LogContext.load(res);
  const signature = req.header(eaveHeaders.EAVE_SIGNATURE_HEADER);
  if (!signature) {
    throw new Error("Missing Eave signature header");
  }

  const eaveSigTsHeader = req.header(eaveHeaders.EAVE_SIG_TS_HEADER);
  if (!eaveSigTsHeader) {
    throw new Error("Missing eave-sig-ts header");
  }

  const eaveSigTs = parseInt(eaveSigTsHeader, 10);
  const now = makeSigTs();
  if (now - eaveSigTs > MAX_SIGNATURE_AGE) {
    throw new Error("expired signature");
  }

  const teamId = req.header(eaveHeaders.EAVE_TEAM_ID_HEADER);
  const accountId = req.header(eaveHeaders.EAVE_ACCOUNT_ID_HEADER);
  const origin = ctx.eave_origin!;

  // let serializedBody;
  // if (typeof req.body === 'string' || req.body instanceof Buffer) {
  //   serializedBody = req.body.toString();
  // } else {
  //   serializedBody = JSON.stringify(req.body, undefined, 0);
  // }

  const payload = (<Buffer>req.body).toString();

  const message = buildMessageToSign({
    method: req.method,
    path: req.originalUrl,
    ts: eaveSigTs,
    requestId: ctx.eave_request_id,
    origin,
    audience,
    payload,
    teamId,
    accountId,
    ctx,
  });

  const signing = Signing.new(origin);
  await signing.verifySignatureOrException(message, signature);
}
