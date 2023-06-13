// import { AddOn, HostClient } from 'atlassian-connect-express';
// import { RequestResponse } from 'request';
// import { promisify } from 'util';
// import { Request } from 'express';
// import eaveLogger from '../logging.js';
// import headers from '../headers.js';
// import { queryConnectInstallation } from '../core-api/operations/connect.js';
// import { AtlassianProduct } from '../core-api/models/connect.js';
// import { EaveOrigin } from '../eave-origins.js';

// export default class ConnectClient {
//   // static async getAuthedConnectClient<T extends ConnectClient>({ req, addon, product, origin }: { req: Request, addon: AddOn, product: AtlassianProduct, origin: EaveOrigin }): Promise<T> {
//   //   const teamId = req.header(headers.EAVE_TEAM_ID_HEADER)!; // presence already validated

//   //   const connectIntegrationResponse = await queryConnectInstallation({
//   //     origin,
//   //     input: {
//   //       connect_integration: {
//   //         product,
//   //         team_id: teamId,
//   //       },
//   //     },
//   //   });

//   //   const client: T = this.getAuthedConnectClientForClientKey(connectIntegrationResponse.connect_integration.client_key, addon);
//   //   return client;
//   // }

//   // private static getAuthedConnectClientForClientKey<T extends ConnectClient>(clientKey: string, addon: AddOn): T {
//   //   const client = addon.httpClient({ clientKey });
//   //   client.get = promisify<any, any>(client.get);
//   //   client.post = promisify<any, any>(client.post);
//   //   client.put = promisify<any, any>(client.put);
//   //   client.del = promisify<any, any>(client.del);
//   //   client.head = promisify<any, any>(client.head);
//   //   client.patch = promisify<any, any>(client.patch);

//   //   return new T(client);
//   // }

//   client: HostClient;

//   constructor(client: HostClient) {
//     this.client = client;
//   }

//   private async request(method: 'get' | 'post' | 'put' | 'del' | 'patch' | 'head', payload: {[key:string]: any}): Promise<RequestResponse> {
//     const finalPayload = {
//       timeout: 1000 * 10, // 10 seconds,
//       ...payload,
//     };

//     const response: RequestResponse = await this.client[method](finalPayload);
//     return response;
//   }

//   private logRequest(name: string, request: any) {
//     eaveLogger.debug({ message: `${name}: request`, request });
//   }

//   private logResponse(name: string, response: RequestResponse) {
//     let message: string;

//     if (response.statusCode < 400) {
//       message = `${name}: response`;
//     } else {
//       message = `${name}: API error`;
//     }

//     eaveLogger.debug({
//       message,
//       body: response.body,
//       statusCode: response.statusCode,
//       requestBody: response.request.body,
//       requestUri: response.request.uri,
//     });
//   }
// }
