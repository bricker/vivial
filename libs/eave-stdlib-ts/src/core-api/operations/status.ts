import { sharedConfig } from '../../config.js';
import { EaveApp } from '../../eave-origins.js';

const baseUrl = sharedConfig.eaveInternalServiceBase(EaveApp.eave_api);

export type StatusResponseBody = {
  service: string;
  version: string;
  status: string;
}

export async function status(): Promise<StatusResponseBody> {
  const resp = await fetch(`${baseUrl}/status`, {
    method: 'get',
  });

  const responseData = <StatusResponseBody>(await resp.json());
  return responseData;
}
