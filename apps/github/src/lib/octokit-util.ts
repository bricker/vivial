import { App, Octokit } from 'octokit';
import eaveLogger, { LogContext } from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { getTeam } from '@eave-fyi/eave-stdlib-ts/src/core-api/operations/team.js';
import { CtxArg } from '@eave-fyi/eave-stdlib-ts/src/requests.js';
import { getGithubInstallation } from '@eave-fyi/eave-stdlib-ts/src/core-api/operations/github.js';
import { EaveApp } from '@eave-fyi/eave-stdlib-ts/src/eave-origins.js';
import { Team } from '@eave-fyi/eave-stdlib-ts/src/core-api/models/team.js';
import { appConfig } from '../config.js';

export async function createOctokitClient(installationId: number): Promise<Octokit> {
  const app = await githubAppClient();
  const octokit = await app.getInstallationOctokit(installationId);
  return octokit;
}

// FIXME: thread safety
let _APP_CLIENT: App | undefined;

export async function githubAppClient(): Promise<App> {
  if (!_APP_CLIENT) {
    const secret = await appConfig.eaveGithubAppWebhookSecret;
    const privateKey = await appConfig.eaveGithubAppPrivateKey;
    const appId = await appConfig.eaveGithubAppId;

    const app = new App({
      appId,
      privateKey,
      webhooks: { secret },
    });

    _APP_CLIENT = app;
  }

  return _APP_CLIENT;
}

export async function getInstallationId(eaveTeamId: string, ctx: LogContext): Promise<number | null> {
  // TODO: Use /integrations/github/query endpoint instead
  const teamResponse = await getTeam({ ctx, origin: appConfig.eaveOrigin, teamId: eaveTeamId });
  const ghIntegration = teamResponse.integrations.github_integration;
  if (!ghIntegration) {
    eaveLogger.error(`GitHub Integration missing for team ${teamResponse.team.id}`, teamResponse, ctx);
    return null;
  }
  return parseInt(ghIntegration.github_install_id, 10);
}

export async function getTeamForInstallation({ installationId, ctx }: CtxArg & { installationId: string }): Promise<Team | null> {
  const response = await getGithubInstallation({
    origin: EaveApp.eave_github_app,
    input: {
      github_integration: {
        github_install_id: installationId,
      },
    },
    ctx,
  });

  if (!response.team) {
    eaveLogger.error('github_install_id not found', response, ctx);
    return null;
  }

  return response.team;
}
