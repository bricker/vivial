import { Router } from "express";
import { AddOn } from "atlassian-connect-express";
import { rawJsonBody } from "@eave-fyi/eave-stdlib-ts/src/middleware/common-middlewares.js";
import { jsonParser } from "@eave-fyi/eave-stdlib-ts/src/middleware/body-parser.js";
import { requireHeaders } from "@eave-fyi/eave-stdlib-ts/src/middleware/require-headers.js";
import { EAVE_ORIGIN_HEADER, EAVE_SIGNATURE_HEADER, EAVE_TEAM_ID_HEADER } from "@eave-fyi/eave-stdlib-ts/src/headers.js";
import { originMiddleware } from "@eave-fyi/eave-stdlib-ts/src/middleware/origin.js";
import { signatureVerification } from "@eave-fyi/eave-stdlib-ts/src/middleware/signature-verification.js";
import { EaveApp } from "@eave-fyi/eave-stdlib-ts/src/eave-origins.js";

export function InternalApiRouter(_args: { addon: AddOn }): Router {
  const router = Router();
  router.use(
    rawJsonBody,
    requireHeaders(EAVE_SIGNATURE_HEADER, EAVE_TEAM_ID_HEADER, EAVE_ORIGIN_HEADER),
    originMiddleware,
    signatureVerification({ audience: EaveApp.eave_jira_app }),
  )

  router.use(jsonParser);

  // Not currently used
  return router;
}
