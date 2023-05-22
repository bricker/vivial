import { Request, Response } from 'express';
import { EmitterWebhookEvent, EmitterWebhookEventName } from '@octokit/webhooks';
import { InstallationLite } from '@octokit/webhooks-types';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { getEaveState } from '@eave-fyi/eave-stdlib-ts/src/lib/request-state.js';
import * as Registry from './registry.js';
import { appConfig } from './config.js';
import pushHandler from './events/push.js';
import { createAppClient } from './lib/octokit-util.js';

Registry.registerHandler('push', pushHandler);

export default async function dispatch(req: Request, res: Response): Promise<void> {
  const id = req.header('x-github-delivery');
  const eventName = req.header('x-github-event') as EmitterWebhookEventName | undefined;
  const signature = req.header('x-hub-signature-256');
  const installationId = req.header('x-github-hook-installation-target-id');

  const eaveState = getEaveState(res);

  const requestBody = (<Buffer>req.body).toString();

  const payload: EmitterWebhookEvent<EmitterWebhookEventName> & {
    installation: InstallationLite,
    action?: string,
  } = JSON.parse(requestBody);

  if (!eventName || !id || !signature || !payload) {
    eaveLogger.error('missing header data from GitHub', eaveState);
    res.status(400).end();
    return;
  }

  const { action } = payload;
  eaveLogger.info('Webhook request', { id, eventName, action, installationId }, eaveState);
  const event = [eventName, action].filter((n) => n).join('.');

  const handler = Registry.getHandler(event);
  if (handler === undefined) {
    eaveLogger.warn(`Event not supported: ${event}`, eaveState);
    res.status(200).end();
    return;
  }

  const app = await createAppClient();

  const verified = await app.webhooks.verify(requestBody, signature);

  if (!verified) {
    eaveLogger.error('signature verification failed', eaveState);

    if (!appConfig.isDevelopment && !appConfig.devMode) {
      res.status(400).end();
      return;
    }
  }

  const octokit = await app.getInstallationOctokit(payload.installation.id);
  await handler(payload, { octokit });
  res.status(200).end();
}
