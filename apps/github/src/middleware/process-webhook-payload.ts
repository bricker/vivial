import Express from 'express';
import { EmitterWebhookEvent, EmitterWebhookEventName } from '@octokit/webhooks';
import { InstallationLite, WebhookEventName } from '@octokit/webhooks-types';
import eaveLogger, { LogContext } from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import registry from '../events/registry.js';
import { appConfig } from '../config.js';
import { createAppClient } from '../lib/octokit-util.js';

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

export type EaveExpressLocals = {
  parsedWebhookPayload: GithubWebhookPayload;
}

function parseWebhookPayload(req: Express.Request): GithubWebhookPayload {
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

export default async function parseAndValidateWebhookPayload(req: Express.Request, res: Express.Response, next: Express.NextFunction): Promise<void> {
  try {
    const ctx = LogContext.load(res);

    const parsedWebhookPayload = parseWebhookPayload(req);
    (<EaveExpressLocals>res.locals).parsedWebhookPayload = parsedWebhookPayload;

    const {
      id,
      signature,
      installationId,
      rawBody,
      parsedBody,
      eventName,
      action,
      fullEventName,
    } = parsedWebhookPayload;

    if (!eventName || !id || !signature || !parsedBody) {
      eaveLogger.error('missing header data from GitHub', ctx);
      res.sendStatus(400);
      return;
    }

    const webhookLogInfo = { id, eventName, action, installationId };
    eaveLogger.info('Webhook request', ctx, webhookLogInfo);

    const handler = registry[fullEventName];
    if (handler === undefined) {
      eaveLogger.warning(`Event not supported: ${fullEventName}`, ctx, webhookLogInfo);
      res.sendStatus(200);
      return;
    }

    const app = await createAppClient();
    const verified = await app.webhooks.verify(rawBody, signature);

    if (!verified) {
      eaveLogger.error('signature verification failed', ctx, webhookLogInfo);

      if (!appConfig.isDevelopment && !appConfig.devMode) {
        // TODO: Add more development safety checks
        res.sendStatus(400);
        return;
      }
    }

    next();
  } catch (e: any) {
    next(e);
  }
}
