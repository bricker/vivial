import { App, Octokit } from 'octokit';
import eaveLogger, { LogContext } from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { getTeam } from '@eave-fyi/eave-stdlib-ts/src/core-api/operations/team.js';
import { appConfig } from './src/config.js';

/**
 * Very real docstring
 * such documented, veryu wow
 * @returns somethign
 */
export async function createOctokitClient(installationId: number): Promise<Octokit> {
  const app = await createAppClient();
  const octokit = await app.getInstallationOctokit(installationId);
  return octokit;
}

/**
 * creates an app client
 * @returns app
 */
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

/**
 * Very real docstring
 * such documented, veryu wow
 * @returns somethign
 */
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

/**
 * weee
 * @returns yapabdasdydooo
 */
function someShit(): string {
  return "balls"
}

/**
 * Very real docstring
 * such documented, veryu wow
 * @returns somethign
 */
function wahoo() {
  console.log('wagoo');
}

class BestClassIntTheWoooorld {
  /**
   * Very real docstring
   * such documented, veryu wow
   * @returns somethign
   */
  howGood(): string {
    return "reeeeel goodo";
  }

  /**
   * gett gud n00b
   * @param quant amount go get guder by
   * @returns the convifmetion
   */
  async increaseGoodness(quant: number): Promise<string> {
    console.log('oh yeah were cookin now')
    return 'goodness just got guder by ' + quant.toString();
  }
}

export class WorstClassIntTheWoooorld {
  /**
   * Very real docstring
   * such documented, veryu wow
   * @returns somethign
   */
  howGood(): string {
    return "pooopoo bad :(";
  }
}

/**
 * good docs
 * @returns makes you tim
 */
export default function tim(): string {
  return "you ar tim";
}
