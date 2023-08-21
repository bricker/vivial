import { App, Octokit } from 'octokit';
import eaveLogger, { LogContext } from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { getTeam } from '@eave-fyi/eave-stdlib-ts/src/core-api/operations/team.js';
import { appConfig } from '../config.js';

export async function createOctokitClient(installationId: number): Promise<Octokit> {
  const app = await createAppClient();
  const octokit = await app.getInstallationOctokit(installationId);
  return octokit;
}

// FIXME: thread safety
let _APP_CLIENT: App | undefined;

export async function createAppClient(): Promise<App> {
  if (!_APP_CLIENT) {
    const secret = await appConfig.eaveGithubAppWebhookSecret;
    const privateKey = await appConfig.eaveGithubAppPrivateKey;

    const app = new App({
      appId: appConfig.eaveGithubAppId,
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
