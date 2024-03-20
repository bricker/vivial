import { Request, Response } from "express";
import { constants as httpConstants } from "node:http2";
import { sharedConfig } from "../config.js";
import { EAVE_DEV_BYPASS_HEADER } from "../headers.js";
import { LogContext, eaveLogger } from "../logging.js";

export function developmentBypassAllowed(
  req: Request,
  _res: Response,
): boolean {
  if (!sharedConfig.isDevelopment) {
    return false;
  }
  if (!sharedConfig.devMode) {
    return false;
  }
  if (sharedConfig.googleCloudProject === "eave-production") {
    return false;
  }

  const devHeader = req.header(EAVE_DEV_BYPASS_HEADER);
  if (!devHeader) {
    return false;
  }

  if (devHeader === "1") {
    return true;
  }

  throw new Error("development bypass failed");
}

export function developmentBypassAuth(req: Request, res: Response): void {
  const ctx = LogContext.load(res);
  eaveLogger.warning("Bypassing auth verification in dev env", ctx);

  const accountId = req.header(httpConstants.HTTP2_HEADER_AUTHORIZATION);
  if (accountId === undefined || typeof accountId !== "string") {
    throw new Error("Authorization header was empty");
  }

  // no account lookup since we cant access orm from ts...

  ctx.eave_account_id = accountId;
}
