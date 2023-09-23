import { NextFunction, Request, Response, Router } from "express";
import { AddOn } from "atlassian-connect-express";
import { rawJsonBody } from "@eave-fyi/eave-stdlib-ts/src/middleware/common-middlewares.js";
import { jsonParser } from "@eave-fyi/eave-stdlib-ts/src/middleware/body-parser.js";
import getAvailableSpaces from "./get-available-spaces.js";
import searchContent from "./search-content.js";
import createContent from "./create-content.js";
import updateContent from "./update-content.js";
import deleteContent from "./delete-content.js";
import ConfluenceClient from "../confluence-client.js";
import { originMiddleware } from "@eave-fyi/eave-stdlib-ts/src/middleware/origin.js";
import { requireHeaders } from "@eave-fyi/eave-stdlib-ts/src/middleware/require-headers.js";
import { signatureVerification } from "@eave-fyi/eave-stdlib-ts/src/middleware/signature-verification.js";
import { EaveApp } from "@eave-fyi/eave-stdlib-ts/src/eave-origins.js";
import { EAVE_ORIGIN_HEADER, EAVE_SIGNATURE_HEADER, EAVE_TEAM_ID_HEADER } from "@eave-fyi/eave-stdlib-ts/src/headers.js";

export function InternalApiRouter({ addon }: { addon: AddOn }): Router {
  const router = Router();
  router.use(
    rawJsonBody,
    requireHeaders(EAVE_SIGNATURE_HEADER, EAVE_TEAM_ID_HEADER, EAVE_ORIGIN_HEADER),
    originMiddleware,
    signatureVerification({ audience: EaveApp.eave_confluence_app }),
  )

  router.use(jsonParser);

  router.post("/spaces/query", async (req: Request, res: Response, next: NextFunction) => {
    try {
      const confluenceClient = await getConfluenceClient(req, res, addon);
      await getAvailableSpaces({ req, res, confluenceClient });
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  router.post("/content/search", async (req: Request, res: Response, next: NextFunction) => {
    try {
      const confluenceClient = await getConfluenceClient(req, res, addon);
      await searchContent({ req, res, confluenceClient });
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  router.post("/content/create", async (req: Request, res: Response, next: NextFunction) => {
    try {
      const confluenceClient = await getConfluenceClient(req, res, addon);
      await createContent({ req, res, confluenceClient });
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  router.post("/content/update", async (req: Request, res: Response, next: NextFunction) => {
    try {
      const confluenceClient = await getConfluenceClient(req, res, addon);
      await updateContent({ req, res, confluenceClient });
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  router.post("/content/delete", async (req: Request, res: Response, next: NextFunction) => {
    try {
      const confluenceClient = await getConfluenceClient(req, res, addon);
      await deleteContent({ req, res, confluenceClient });
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  // internalApiRouter.all('/proxy', async (/* req: Request, res: Response */) => {
  //   // TODO: Confluence API proxy?
  // });

  return router;
}

async function getConfluenceClient(req: Request, _res: Response, addon: AddOn): Promise<ConfluenceClient> {
  const teamId = req.header(EAVE_TEAM_ID_HEADER)!; // presence already validated
  const client = await ConfluenceClient.getAuthedConfluenceClient({
    addon,
    teamId,
  });
  return client;
}
