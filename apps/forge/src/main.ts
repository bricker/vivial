import './polyfill';

import fs from 'fs';
import { EaveForgeInboundOperation } from '@eave-fyi/eave-stdlib-ts/src/core-api/enums.js';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import createDocument from './api/create-document.js';
import updateDocument from './api/update-document.js';
import archiveDocument from './api/archive-document.js';
import { makeResponse } from './response.js';
import { InstalledAppEventPayload, UpgradedAppEventPayload, CommentedIssueEventPayload, WebTriggerRequestPayload, WebTriggerResponsePayload, EventPayload } from './types.js';
import appConfig from './config.js';
import jiraCommentedIssueEventHandler from './events/jira-commented-issue.js';
import forgeInstalledAppEventHandler from './events/forge-installed-app.js';
import forgeUpgradedAppEventHandler from './events/forge-upgraded-app.js';

export async function forgeEventDispatch(event: EventPayload) {
  putGCPServiceAccountKey();
  const { eventType } = event;
  eaveLogger.info(`event received: ${eventType}`, {
    ...event,
    context: null, // logging this is too noisy
    cloudId: event.context?.cloudId,
    moduleKey: event.context?.moduleKey,
  });

  switch (eventType) {
    case 'avi:forge:installed:app':
      await forgeInstalledAppEventHandler(<InstalledAppEventPayload>event);
      break;
    case 'avi:forge:upgraded:app':
      await forgeUpgradedAppEventHandler(<UpgradedAppEventPayload>event);
      break;
    case 'avi:jira:commented:issue':
      await jiraCommentedIssueEventHandler(<CommentedIssueEventPayload>event);
      break;
    default:
      eaveLogger.warning(`No event handler for event ${eventType}`, event);
  }
}

export async function eaveApiDispatch(request: WebTriggerRequestPayload): Promise<WebTriggerResponsePayload> {
  // TODO: Signature validation
  putGCPServiceAccountKey();
  eaveLogger.info('eaveInbound', request);
  if (!request.body) {
    eaveLogger.error('Missing request body');
    return makeResponse({ statusCode: 400 });
  }

  const body = JSON.parse(request.body);
  switch (body.operation) {
    case EaveForgeInboundOperation.createDocument:
      return createDocument(request);
    case EaveForgeInboundOperation.updateDocument:
      return updateDocument(request);
    case EaveForgeInboundOperation.archiveDocument:
      return archiveDocument(request);
    default:
      eaveLogger.error(`Unsupported operation: ${body.operation}`);
      return makeResponse({ statusCode: 400 });
  }

  return makeResponse();
}

function putGCPServiceAccountKey() {
  // GCP client libraries require application credentials to be in a file, so we have to write it to a file every time.
  // Alternatively, we could bundle the service account key with the app on each deployment.
  fs.writeFileSync(appConfig.googleApplicationCredentialsFile, appConfig.eaveGCPServiceAccountCredentials);
}
