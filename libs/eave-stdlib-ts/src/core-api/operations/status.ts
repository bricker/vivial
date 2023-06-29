import { sharedConfig } from '../../config.js';
import { EaveService } from '../../eave-origins.js';

const baseUrl = sharedConfig.eaveInternalServiceBase(EaveService.api);

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
