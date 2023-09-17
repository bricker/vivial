import { sharedConfig } from '../../config.js';
import { EaveApp } from '../../eave-origins.js';
import { CORE_API_BASE_URL } from './shared.js';

export type StatusResponseBody = {
  service: string;
  version: string;
  status: string;
}

export async function status(): Promise<StatusResponseBody> {
  const resp = await fetch(`${CORE_API_BASE_URL}/status`, {
    method: 'get',
  });

  const responseData = <StatusResponseBody>(await resp.json());
  return responseData;
}
