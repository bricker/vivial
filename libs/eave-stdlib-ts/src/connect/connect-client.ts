import { AddOn, HostClient } from 'atlassian-connect-express';
import { CoreOptions, RequestResponse, UrlOptions } from 'request';
import { promisify } from 'util';
import { Request } from 'express';
import eaveLogger from '../logging.js';
import headers from '../headers.js';
import { queryConnectInstallation } from '../core-api/operations/connect.js';
import { AtlassianProduct } from '../core-api/models/connect.js';
import { EaveOrigin } from '../eave-origins.js';

export type RequestOpts = CoreOptions & UrlOptions;

export default class ConnectClient {
  static async getAuthedConnectClient({ req, addon, product, origin }: { req: Request, addon: AddOn, product: AtlassianProduct, origin: EaveOrigin }): Promise<HostClient> {
    const teamId = req.header(headers.EAVE_TEAM_ID_HEADER)!; // presence already validated

    const connectIntegrationResponse = await queryConnectInstallation({
      origin,
      input: {
        connect_integration: {
          product,
          team_id: teamId,
        },
      },
    });

    const client = this.getAuthedConnectClientForClientKey(connectIntegrationResponse.connect_integration.client_key, addon);
    return client;
  }

  private static getAuthedConnectClientForClientKey(clientKey: string, addon: AddOn): HostClient {
    const client = addon.httpClient({ clientKey });
    client.get = promisify<any, any>(client.get);
    client.post = promisify<any, any>(client.post);
    client.put = promisify<any, any>(client.put);
    client.del = promisify<any, any>(client.del);
    client.head = promisify<any, any>(client.head);
    client.patch = promisify<any, any>(client.patch);

    return client;
  }

  client: HostClient;

  constructor(client: HostClient) {
    this.client = client;
  }

  async request(method: 'get' | 'post' | 'put' | 'del' | 'patch' | 'head', payload: RequestOpts): Promise<RequestResponse> {
    const finalPayload = {
      timeout: 1000 * 10, // 10 seconds,
      ...payload,
    };

    this.logRequest(payload);
    const response: RequestResponse = await this.client[method](finalPayload);
    this.logResponse(response);
    return response;
  }

  private logRequest(request: RequestOpts) {
    const url = request.url;
    eaveLogger.debug({ message: `Request: ${url}`, request });
  }

  private logResponse(response: RequestResponse) {
    let message: string;
    let level: 'info' | 'warning';

    const url = response.request.uri.href;

    if (response.statusCode < 400) {
      level = 'info';
      message = `Response: ${url}`;
    } else {
      level = 'warning';
      const { statusCode, message: errorMessage } = response.body || {};
      message = `API error: ${url} (${statusCode}) ${errorMessage}`;
    }

    eaveLogger[level]({
      message,
      statusCode: response.statusCode,
      requestUri: response.request.uri.href,
    });
  }
}
