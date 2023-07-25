import { Request, Response } from 'express';
import { EmitterWebhookEvent, EmitterWebhookEventName } from '@octokit/webhooks';
import { InstallationLite } from '@octokit/webhooks-types';
import eaveLogger, { LogContext } from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import * as Registry from './registry.js';
import { appConfig } from './config.js';
import pushHandler from './events/push.js';
import { createAppClient } from './lib/octokit-util.js';

Registry.registerHandler('push', pushHandler);

export default async function dispatch(req: Request, res: Response): Promise<void> {
  const ctx = LogContext.load(res);
  const id = req.header('x-github-delivery');
  const eventName = req.header('x-github-event') as EmitterWebhookEventName | undefined;
  const signature = req.header('x-hub-signature-256');
  const installationId = req.header('x-github-hook-installation-target-id');

  const requestBody = (<Buffer>req.body).toString();

  const payload: EmitterWebhookEvent<EmitterWebhookEventName> & {
    installation: InstallationLite,
    action?: string,
  } = JSON.parse(requestBody);

  if (!eventName || !id || !signature || !payload) {
    eaveLogger.error('missing header data from GitHub', ctx);
    res.sendStatus(400);
    return;
  }

  const { action } = payload;
  const webhookInfo = { id, eventName, action, installationId };
  eaveLogger.info('Webhook request', ctx, webhookInfo);
  const event = [eventName, action].filter((n) => n).join('.');

  const handler = Registry.getHandler(event);
  if (handler === undefined) {
    eaveLogger.warning(`Event not supported: ${event}`, ctx, webhookInfo);
    res.sendStatus(200);
    return;
  }

  const app = await createAppClient();
  const verified = await app.webhooks.verify(requestBody, signature);

  if (!verified) {
    eaveLogger.error('signature verification failed', ctx);

    if (!appConfig.isDevelopment && !appConfig.devMode) {
      res.sendStatus(400);
      return;
    }
  }

  const octokit = await app.getInstallationOctokit(payload.installation.id);
  await handler(payload, { octokit, ctx });
  res.sendStatus(200);
}
