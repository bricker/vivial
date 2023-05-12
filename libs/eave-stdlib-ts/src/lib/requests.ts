import { RequestInit } from 'node-fetch';
import { computeSignature } from './signing';

export async function initRequest(data: unknown, teamId?: string): Promise<RequestInit> {
  const payload = JSON.stringify(data);
  const signature = await computeSignature(payload, teamId);
  const headers: { [key: string]: string } = {
    'content-type': 'application/json',
    'eave-signature': signature,
  };

  if (teamId !== undefined) {
    headers['eave-team-id'] = teamId;
  }

  return {
    method: 'post',
    body: payload,
    headers,
  };
}