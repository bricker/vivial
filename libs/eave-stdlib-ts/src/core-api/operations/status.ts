import { sharedConfig } from '../../config.js';
import { EaveApp } from '../../eave-origins.js';
import { CoreApiEndpointConfiguration } from './shared.js';

export type StatusResponseBody = {
  service: string;
  version: string;
  status: string;
}

export class StatusOperation {
  static config = new CoreApiEndpointConfiguration({ path: "/status" })

  static async perform(): Promise<StatusResponseBody> {
    const resp = await fetch(this.config.url, {
      method: 'get',
    });

    const responseData = <StatusResponseBody>(await resp.json());
    return responseData;
  }
}