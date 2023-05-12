import { App, Octokit } from 'octokit';
import * as eaveClient from '@eave-fyi/eave-stdlib-ts/src/core-api/client.js';
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
  const teamResponse = await eaveClient.getTeam(eaveTeamId);
  const ghIntegration = teamResponse.integrations.github;
  if (ghIntegration !== undefined) {
    return parseInt(ghIntegration.github_install_id, 10);
  }
  return null;
}
