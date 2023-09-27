import { MissingRequiredHeaderError } from "@eave-fyi/eave-stdlib-ts/src/exceptions.js";
import { EAVE_CRON_DISPATCH_KEY_HEADER } from "@eave-fyi/eave-stdlib-ts/src/headers.js";
import {
  LogContext,
  eaveLogger,
} from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import Express from "express";
import { verifyCronSecret } from "../middleware/verify-cron-secret.js";
import { getCronHandler } from "./cron-registry.js";

export async function cronDispatchHandler(
  req: Express.Request,
  res: Express.Response,
  next: Express.NextFunction,
): Promise<void> {
  await verifyCronSecret(req);

  const ctx = LogContext.load(res);
  const dispatchKey = req.header(EAVE_CRON_DISPATCH_KEY_HEADER)?.toLowerCase();
  if (!dispatchKey) {
    throw new MissingRequiredHeaderError(EAVE_CRON_DISPATCH_KEY_HEADER);
  }

  const handler = getCronHandler({ dispatchKey });
  if (!handler) {
    eaveLogger.warning(`Handler not found for dispatchKey ${dispatchKey}`, ctx);
    return;
  }

  await handler(req, res, next);
}
