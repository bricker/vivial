import { NextFunction, Request, Response, Router } from "express";
import { getSummary } from "./content.js";
import { subscribe } from "./subscribe.js";
import { createPullRequest } from "./create-pull-request.js";
import { GetGithubUrlContentOperation } from "@eave-fyi/eave-stdlib-ts/src/github-api/operations/get-content.js";
import { CreateGithubResourceSubscriptionOperation } from "@eave-fyi/eave-stdlib-ts/src/github-api/operations/create-subscription.js";
import { CreateGithubPullRequestOperation } from "@eave-fyi/eave-stdlib-ts/src/github-api/operations/create-pull-request.js";
import { Octokit } from "octokit";
import headers from '@eave-fyi/eave-stdlib-ts/src/headers.js';
import eaveLogger, { LogContext } from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { createOctokitClient, getInstallationId } from '../lib/octokit-util.js';


export function InternalApiRouter(): Router {
  const router = Router();

  router.post(GetGithubUrlContentOperation.config.path, ...GetGithubUrlContentOperation.config.middlewares, async (req: Request, res: Response, next: NextFunction) => {
    try {
      const ctx = LogContext.load(res);
      const octokit = await buildOctokitClient(req, res, ctx);
      if (octokit) {
        await getSummary({ req, res, octokit, ctx });
      }
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  router.post(CreateGithubResourceSubscriptionOperation.config.path, ...CreateGithubResourceSubscriptionOperation.config.middlewares, async (req: Request, res: Response, next: NextFunction) => {
    try {
      const ctx = LogContext.load(res);
      const octokit = await buildOctokitClient(req, res, ctx);
      if (octokit) {
        await subscribe({ req, res, octokit, ctx });
      }
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  router.post(CreateGithubPullRequestOperation.config.path, ...CreateGithubPullRequestOperation.config.middlewares, async (req: Request, res: Response, next: NextFunction) => {
    try {
      const ctx = LogContext.load(res);
      const octokit = await buildOctokitClient(req, res, ctx);
      if (octokit) {
        await createPullRequest({ req, res, octokit, ctx });
      }
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  return router;
}

async function buildOctokitClient(req: Request, res: Response, ctx: LogContext): Promise<Octokit | null> {
  const eaveTeamId = req.header(headers.EAVE_TEAM_ID_HEADER)!; // presence already validated by middleware

  const installationId = await getInstallationId(eaveTeamId, ctx);
  if (installationId === null) {
    eaveLogger.error('missing github installation id', ctx);
    res.sendStatus(500);
    return null;
  }
  const client = await createOctokitClient(installationId);
  return client;
}
