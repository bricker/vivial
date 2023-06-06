import { App, Octokit } from 'octokit';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { getTeam } from '@eave-fyi/eave-stdlib-ts/src/core-api/operations/team.js';
import { appConfig } from '../config.js';

export async function createOctokitClient(installationId: number): Promise<Octokit> {
  const app = await createAppClient();
  const octokit = await app.getInstallationOctokit(installationId);
  return octokit;
}

export async function createAppClient(): Promise<App> {
  const secret = await appConfig.eaveGithubAppWebhookSecret;
  const privateKey = await appConfig.eaveGithubAppPrivateKey;

  const app = new App({
    appId: appConfig.eaveGithubAppId,
    privateKey,
    webhooks: { secret },
  });
  return app;
}

export async function getInstallationId(eaveTeamId: string): Promise<number | null> {
  // TODO: Use /integrations/github/query endpoint instead
  const teamResponse = await getTeam({ origin: appConfig.eaveOrigin, teamId: eaveTeamId });
  const ghIntegration = teamResponse.integrations.github_integration;
  if (!ghIntegration) {
    eaveLogger.error(`GitHub Integration missing for team ${teamResponse.team.id}`, teamResponse);
    return null;
  }
  return parseInt(ghIntegration.github_install_id, 10);
}
