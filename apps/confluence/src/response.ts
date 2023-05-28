import { WebTriggerResponsePayload } from './types';

export function makeResponse(
  { statusCode = 200, statusText, body = {} }:
  { statusCode?: number, statusText?: string, body?: {[key: string]: unknown} } = {}): WebTriggerResponsePayload {
  return {
    body: JSON.stringify(body),
    headers: {
      'Content-Type': ['application/json'],
    },
    statusCode,
    statusText: statusText || `${statusCode}`,
  };
}
