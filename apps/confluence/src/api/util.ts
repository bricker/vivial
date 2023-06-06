import { promisify } from 'util';
import { Request } from 'express';
import { AddOn, HostClient } from 'atlassian-connect-express';
import headers from '@eave-fyi/eave-stdlib-ts/src/headers.js';
import { queryConnectInstallation } from '@eave-fyi/eave-stdlib-ts/src/core-api/operations/connect.js';
import { AtlassianProduct } from '@eave-fyi/eave-stdlib-ts/src/core-api/models/connect.js';
import html from 'html-entities';
import appConfig from '../config.js';

export async function getAuthedConnectClient(req: Request, addon: AddOn): Promise<HostClient> {
  const teamId = req.header(headers.EAVE_TEAM_ID_HEADER)!; // presence already validated

  const connectIntegrationResponse = await queryConnectInstallation({
    origin: appConfig.eaveOrigin,
    input: {
      connect_integration: {
        product: AtlassianProduct.confluence,
        team_id: teamId,
      },
    },
  });

  return getAuthedConnectClientForClientKey(connectIntegrationResponse.connect_integration.client_key, addon);
}

export async function getAuthedConnectClientForClientKey(clientKey: string, addon: AddOn): Promise<HostClient> {
  const client = addon.httpClient({ clientKey });
  client.get = promisify<any, any>(client.get);
  client.post = promisify<any, any>(client.post);
  client.put = promisify<any, any>(client.put);
  client.del = promisify<any, any>(client.del);
  client.head = promisify<any, any>(client.head);
  client.patch = promisify<any, any>(client.patch);
  return client;
}

// Fixes some HTML things that Confluence chokes on
export function cleanDocument(document: string): string {
  let content = html.decode(document);
  content = content.replace(/&/g, '&amp;'); // confluence can't handle decoded ampersands
  content = content.replace(/<br>/gi, '<br/>'); // confluence can't handle unclosed br tags
  return content;
}
