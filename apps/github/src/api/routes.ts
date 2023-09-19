import { NextFunction, Request, Response, Router } from "express";
import { getSummary } from "./content.js";
import { subscribe } from "./subscribe.js";
import { createPullRequest } from "./create-pull-request.js";
import { GetGithubUrlContentOperation } from "@eave-fyi/eave-stdlib-ts/src/github-api/operations/get-content.js";
import { CreateGithubResourceSubscriptionOperation } from "@eave-fyi/eave-stdlib-ts/src/github-api/operations/create-subscription.js";
import { CreateGithubPullRequestOperation } from "@eave-fyi/eave-stdlib-ts/src/github-api/operations/create-pull-request.js";

export function InternalApiRouter(): Router {
  const router = Router();

  router.post(GetGithubUrlContentOperation.config.subPath, ...GetGithubUrlContentOperation.config.middlewares, async (req: Request, res: Response, next: NextFunction) => {
    try {
      await getSummary(req, res);
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  router.post(CreateGithubResourceSubscriptionOperation.config.subPath, ...CreateGithubResourceSubscriptionOperation.config.middlewares, async (req: Request, res: Response, next: NextFunction) => {
    try {
      await subscribe(req, res);
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  router.post(CreateGithubPullRequestOperation.config.subPath, ...CreateGithubPullRequestOperation.config.middlewares, async (req: Request, res: Response, next: NextFunction) => {
    try {
      await createPullRequest(req, res);
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  return router;
}
