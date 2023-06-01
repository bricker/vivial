import { sharedConfig } from '../../config.js';

export type StatusResponseBody = {
  service: string;
  version: string;
  status: string;
}

export async function status(): Promise<StatusResponseBody> {
  const resp = await fetch(`${sharedConfig.eaveApiBase}/status`, {
    method: 'get',
  });

  const responseData = <StatusResponseBody>(await resp.json());
  return responseData;
}
