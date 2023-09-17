import { NextFunction, Request, Response, Router } from "express";
import * as GetGithubUrlContent from "@eave-fyi/eave-stdlib-ts/src/github-api/operations/get-content.js";
import * as CreateGithubResourceSubscription from "@eave-fyi/eave-stdlib-ts/src/github-api/operations/create-subscription.js";
import * as CreateGithubPullRequest from "@eave-fyi/eave-stdlib-ts/src/github-api/operations/create-pull-request.js";
import { getSummary } from "./content.js";
import { subscribe } from "./subscribe.js";
import { createPullRequest } from "./create-pull-request.js";

export function InternalApiRouter(): Router {
  const router = Router();

  router.post(GetGithubUrlContent.config.path, ...GetGithubUrlContent.config.middlewares, async (req: Request, res: Response, next: NextFunction) => {
    try {
      await getSummary(req, res);
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  router.post(CreateGithubResourceSubscription.config.path, ...CreateGithubResourceSubscription.config.middlewares, async (req: Request, res: Response, next: NextFunction) => {
    try {
      await subscribe(req, res);
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  router.post(CreateGithubPullRequest.config.path, ...CreateGithubPullRequest.config.middlewares, async (req: Request, res: Response, next: NextFunction) => {
    try {
      await createPullRequest(req, res);
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  return router;
}
