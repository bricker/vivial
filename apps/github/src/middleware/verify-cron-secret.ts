import { Request } from "express";
import { appConfig } from "../config.js";
import { EAVE_CRON_SHARED_SECRET_HEADER } from "@eave-fyi/eave-stdlib-ts/src/headers.js";
import { MissingRequiredHeaderError, InvalidSignatureError } from "@eave-fyi/eave-stdlib-ts/src/exceptions.js";

export async function verifyCronSecret(req: Request): Promise<void> {
  const sharedSecret = await appConfig.eaveGithubAppCronSecret;
  const sharedSecretHeader = req.header(EAVE_CRON_SHARED_SECRET_HEADER);
  if (!sharedSecretHeader) {
    throw new MissingRequiredHeaderError(EAVE_CRON_SHARED_SECRET_HEADER);
  }

  if (sharedSecret !== sharedSecretHeader) {
    throw new InvalidSignatureError(EAVE_CRON_SHARED_SECRET_HEADER);
  }
}
