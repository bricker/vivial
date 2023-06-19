import { AddOn, HostClient } from 'atlassian-connect-express';
import { CoreOptions, RequestResponse, UrlOptions } from 'request';
import { promisify } from 'util';
import { Request } from 'express';
import eaveLogger, { LogContext } from '../logging.js';
import { queryConnectInstallation } from '../core-api/operations/connect.js';
import { AtlassianProduct } from '../core-api/models/connect.js';
import { EaveOrigin } from '../eave-origins.js';

export type RequestOpts = CoreOptions & UrlOptions;

export default class ConnectClient {
  static async getAuthedConnectClient({
    addon,
    product,
    origin,
    teamId,
    clientKey,
  }: {
    req: Request,
    addon: AddOn,
    product: AtlassianProduct,
    origin: EaveOrigin,
    teamId?: string,
    clientKey?: string,
  }): Promise<HostClient> {
    if (!clientKey) {
      const connectIntegrationResponse = await queryConnectInstallation({
        origin,
        input: {
          connect_integration: {
            product,
            team_id: teamId,
          },
        },
      });

      // eslint-disable-next-line no-param-reassign
      clientKey = connectIntegrationResponse.connect_integration.client_key;
    }

    const client = this.getAuthedConnectClientForClientKey(clientKey, addon);
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

  async request(method: 'get' | 'post' | 'put' | 'del' | 'patch' | 'head', payload: RequestOpts, ctx?: LogContext): Promise<RequestResponse> {
    const finalPayload = {
      timeout: 1000 * 120,
      ...payload,
    };

    this.logRequest(payload, ctx);
    const response: RequestResponse = await this.client[method](finalPayload);
    this.logResponse(response, ctx);
    return response;
  }

  private logRequest(request: RequestOpts, ctx?: LogContext) {
    const url = request.url;
    eaveLogger.debug(`[connect client] Request: ${url}`, ctx);
  }

  private logResponse(response: RequestResponse, ctx?: LogContext) {
    const url = response.request.uri.href;

    if (response.statusCode < 400) {
      eaveLogger.info(
        `[connect client] Response: ${url}`,
        {
          statusCode: response.statusCode,
          requestUri: response.request.uri.href,
        },
        ctx,
      );
    } else {
      const { errors: validationErrors, errorMessages } = response.body || {};
      const errors = { validationErrors, errorMessages };
      const messages = JSON.stringify(errors);

      eaveLogger.warning(
        `[connect client] API error: ${url} (${response.statusCode}) ${messages}`,
        {
          statusCode: response.statusCode,
          requestUri: response.request.uri.href,
          errors,
        },
        ctx,
      );
    }

    eaveLogger.debug(
      '[connect client] response body',
      { body: response.body },
      ctx,
    );
  }
}
