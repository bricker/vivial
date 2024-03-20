import { Team } from "@eave-fyi/eave-stdlib-ts/src/core-api/models/team.js";
import { QueryGithubInstallationOperation } from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/github-installation.js";
import { EaveApp } from "@eave-fyi/eave-stdlib-ts/src/eave-origins.js";
import { EAVE_TEAM_ID_HEADER } from "@eave-fyi/eave-stdlib-ts/src/headers.js";
import {
  LogContext,
  eaveLogger,
} from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import { CtxArg } from "@eave-fyi/eave-stdlib-ts/src/requests.js";
import Express from "express";
import { App, Octokit } from "octokit";
import { appConfig } from "../config.js";

export async function createOctokitClient(
  installationId: number,
): Promise<Octokit> {
  const app = await githubAppClient();
  const octokit = await app.getInstallationOctokit(installationId);
  return octokit;
}

export async function createTeamOctokitClient(
  req: Express.Request,
  ctx: LogContext,
): Promise<Octokit> {
  const eaveTeamId = req.header(EAVE_TEAM_ID_HEADER)!; // presence already validated by middleware

  const installationId = await getInstallationId(eaveTeamId, ctx);
  if (installationId === null) {
    throw new Error("missing github installation id");
  }
  const client = await createOctokitClient(installationId);
  return client;
}

// FIXME: thread safety
let _APP_CLIENT: App | undefined;

export async function githubAppClient(): Promise<App> {
  if (!_APP_CLIENT) {
    const secret = await appConfig.eaveGithubAppWebhookSecret;
    const privateKey = await appConfig.eaveGithubAppPrivateKey;
    const appId = await appConfig.eaveGithubAppId;
    const clientId = await appConfig.eaveGithubAppClientId;
    const clientSecret = await appConfig.eaveGithubAppClientSecret;

    const app = new App({
      appId,
      privateKey,
      webhooks: { secret },
      oauth: { clientId, clientSecret },
    });

    _APP_CLIENT = app;
  }

  return _APP_CLIENT;
}

export async function getInstallationId(
  eaveTeamId: string,
  ctx: LogContext,
): Promise<number | null> {
  const response = await QueryGithubInstallationOperation.perform({
    ctx,
    origin: appConfig.eaveOrigin,
    input: {
      team: {
        id: eaveTeamId,
      },
    },
  });
  const installation = response.github_installation;
  if (!installation) {
    eaveLogger.error(
      `GitHub Integration missing for team ${eaveTeamId}`,
      response,
      ctx,
    );
    return null;
  }
  return parseInt(installation.github_install_id, 10);
}

export async function getTeamForInstallation({
  installationId,
  ctx,
}: CtxArg & { installationId: string | number }): Promise<Team | null> {
  const response = await QueryGithubInstallationOperation.perform({
    origin: EaveApp.eave_github_app,
    input: {
      github_installation: {
        github_install_id: installationId.toString(),
      },
    },
    ctx,
  });

  if (!response.team) {
    eaveLogger.error("github_install_id not found", response, ctx);
    return null;
  }

  return response.team;
}
