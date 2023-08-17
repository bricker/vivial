import { Request, Response, NextFunction } from 'express';
import { EmitterWebhookEvent, EmitterWebhookEventName } from '@octokit/webhooks';
import { InstallationLite } from '@octokit/webhooks-types';
import eaveLogger, { LogContext } from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import Registry from './registry.js';
import { appConfig } from '../config.js';
import { createAppClient } from '../lib/octokit-util.js';

export default async function verifyWebhookPayload(req: Request, res: Response, next: NextFunction): Promise<void> {
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

  const handler = Registry[event];
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
      // TODO: Add more development safety checks
      res.sendStatus(400);
      return;
    }
  }

  // TODO: Handoff to background
  res.sendStatus(200);
}
