import { Request, Response } from 'express';
import { EmitterWebhookEvent, EmitterWebhookEventName } from '@octokit/webhooks';
import { InstallationLite } from '@octokit/webhooks-types';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging';
import * as Registry from './registry';
import { appConfig } from './config';
import pushHandler from './events/push';
import { createAppClient } from './lib/octokit-util';

Registry.registerHandler('push', pushHandler);

export default async function dispatch(req: Request, res: Response): Promise<void> {
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
    res.status(400).end();
    return;
  }

  const { action } = payload;
  eaveLogger.info({ id, eventName, action, installationId });
  const event = [eventName, action].filter((n) => n).join('.');

  const handler = Registry.getHandler(event);
  if (handler === undefined) {
    eaveLogger.warn('Event not supported:', event);
    res.status(200).end();
    return;
  }

  const app = await createAppClient();

  const verified = await app.webhooks.verify(requestBody, signature);

  if (!verified) {
    eaveLogger.warn('signature verification failed');

    if (!appConfig.isDevelopment && !appConfig.devMode) {
      res.status(400).end();
      return;
    }
  }

  const octokit = await app.getInstallationOctokit(payload.installation.id);
  await handler(payload, { octokit });
  res.status(200).end();
}
