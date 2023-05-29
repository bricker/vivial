import './polyfill';

import fs from 'fs';
import { webTrigger } from '@forge/api';
import { EaveForgeInboundOperation } from '@eave-fyi/eave-stdlib-ts/src/core-api/enums.js';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import createDocument from './api/create-document.js';
import updateDocument from './api/update-document.js';
import archiveDocument from './api/archive-document.js';
import { makeResponse } from './response.js';
import { InstalledAppEventPayload, UpgradedAppEventPayload, CommentedIssueEventPayload, WebTriggerRequestPayload, WebTriggerResponsePayload, EventPayload } from './types.js';
import appConfig from './config.js';
import jiraCommentedIssueEventHandler from './events/jira-commented-issue.js';

const WEBTRIGGER_KEY = 'webtrigger-eaveApi';

export async function forgeInstalledApp(event: InstalledAppEventPayload) {
  const { registerForgeInstallation } = await import('@eave-fyi/eave-stdlib-ts/src/core-api/operations/forge.js');

  putGCPServiceAccountKey();
  eaveLogger.info('forgeInstalledApp', event);
  const webtriggerUrl = await webTrigger.getUrl(WEBTRIGGER_KEY);
  const resp = await registerForgeInstallation(appConfig.eaveOrigin, {
    forge_integration: {
      // atlassian_cloud_id: event['context']['cloudId'], // TODO Is this correct?
      forge_app_id: event.app.id,
      forge_app_version: event.app.version,
      forge_app_installation_id: event.id,
      forge_app_installer_account_id: event.installerAccountId,
      webtrigger_url: webtriggerUrl,
    },
  });

  eaveLogger.info('core API response', resp);
}

export async function forgeUpgradedApp(event: UpgradedAppEventPayload) {
  putGCPServiceAccountKey();
  eaveLogger.info('forgeUpgradedApp', event);
  return makeResponse({
    statusCode: 200,
    body: {},
  });
}

export async function forgeEventDispatch(event: EventPayload) {
  putGCPServiceAccountKey();
  eaveLogger.info('event received', event);

  const { eventType } = event;

  switch (eventType) {
    case 'avi:jira:commented:issue':
      return jiraCommentedIssueEventHandler(<CommentedIssueEventPayload>event);
    default:
      eaveLogger.warning(`No event handler for event ${eventType}`, event);
      return makeResponse({
        statusCode: 200,
        body: {},
      });
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

  return makeResponse({
    statusCode: 200,
    body: {},
  });
}

function putGCPServiceAccountKey(): void {
  fs.writeFileSync(appConfig.googleApplicationCredentialsFile, appConfig.eaveGCPServiceAccountCredentials);
}
