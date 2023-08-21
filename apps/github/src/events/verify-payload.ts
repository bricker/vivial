import { Request, Response, NextFunction } from 'express';
import { EmitterWebhookEvent, EmitterWebhookEventName } from '@octokit/webhooks';
import { InstallationLite } from '@octokit/webhooks-types';
import eaveLogger, { LogContext } from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import registry from './registry.js';
import { appConfig } from '../config.js';
import { createAppClient, parseWebhookPayload } from '../lib/octokit-util.js';

export default async function verifyWebhookPayload(req: Request, res: Response, next: NextFunction): Promise<void> {
  const ctx = LogContext.load(res);
  const {
    id,
    signature,
    installationId,
    rawBody,
    parsedBody,
    eventName,
    action,
    fullEventName,
  } = parseWebhookPayload(req);

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
}
