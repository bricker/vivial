import { Request } from 'express';
import { App, Octokit } from 'octokit';
import { EmitterWebhookEvent, EmitterWebhookEventName } from '@octokit/webhooks';
import { InstallationLite, WebhookEventName } from '@octokit/webhooks-types';
import eaveLogger, { LogContext } from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { getTeam } from '@eave-fyi/eave-stdlib-ts/src/core-api/operations/team.js';
import { appConfig } from '../config.js';

type GithubWebhookBody = EmitterWebhookEvent<EmitterWebhookEventName> & {
  installation: InstallationLite,
  action?: string,
}

type GithubWebhookPayload = {
  id?: string,
  signature?: string,
  installationId?: string,
  rawBody: string,
  parsedBody: GithubWebhookBody,
  eventName?: WebhookEventName,
  action?: string,
  fullEventName: string,
};

export function parseWebhookPayload(req: Request): GithubWebhookPayload {
  const id = req.header('x-github-delivery');

  /*
    This header contains the "WebhookEventName", which is what Github calls it but is a misnomer imo.
    An "Event" (available in the headers) in this context is the object type. For example: "issues", "pull_request", "milestone".
    An "Action" (available in the request body) is the, er, action that triggered the webhook. For example: "created", "closed", "edited".
    So, an app subscribes to "Events", which includes all of its "Actions".
    To add more confusion, some "Events" are actually Events and don't have any "Actions", like the "push" event.
    But, generally, you can think of the "Event" (in Github terms) to be the subject of the action, and the "Action" to be the trigger.
    It seems silly to separate the "Event" and "Action" values, because one is useless without the other.
  */
  const eventName = req.header('x-github-event') as WebhookEventName | undefined;
  const signature = req.header('x-hub-signature-256');
  const installationId = req.header('x-github-hook-installation-target-id');

  const rawBody = (<Buffer>req.body).toString();
  const parsedBody: GithubWebhookBody = JSON.parse(rawBody);

  const { action } = parsedBody;
  const fullEventName = [eventName, action].filter((n) => n).join('.');

  return {
    id,
    signature,
    installationId,
    rawBody,
    parsedBody,
    eventName,
    action,
    fullEventName,
  };
}

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
