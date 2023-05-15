import fetch, { Response } from 'node-fetch';
import { v4 as uuid4 } from 'uuid';
import { EaveOrigin } from '../eave-origins.js';
import { getKey, signBase64 } from '../signing.js';
import eaveHeaders from '../headers.js';
import {
  NotFoundError,
  UnauthorizedError,
  BadRequestError,
  InternalServerError,
  HTTPException
} from '../exceptions.js';
import { sharedConfig } from '../config.js';


let ORIGIN: EaveOrigin;

export function setOrigin(origin: EaveOrigin): void {
  ORIGIN = origin;
}

export function getOrigin(): EaveOrigin {
  return ORIGIN;
}

export function buildMessageToSign(
  method: string,
  url: string,
  requestId: string,
  origin: EaveOrigin | string,
  payload: string,
  teamId?: string,
  accountId?: string,
): string {
  const signatureElements = [
    origin,
    method,
    url,
    requestId,
    payload,
  ]

  if (teamId !== undefined) {
    signatureElements.push(teamId);
  }
  if (accountId !== undefined) {
    signatureElements.push(accountId);
  }

  return signatureElements.join(':');
}

export async function makeRequest(
  path: string,
  input?: unknown,
  base?: string,
  accessToken?: string,
  teamId?: string,
  accountId?: string,
  method: string = 'post',
): Promise<Response> {
  if (base === undefined) {
    base = sharedConfig.eaveApiBase;
  }
  const url = new URL(path, base).href;
  const requestId = uuid4();

  const payload = JSON.stringify(input);
  const message = buildMessageToSign(
    method, 
    url, 
    requestId, 
    ORIGIN, 
    input === undefined ? '' : JSON.stringify(input), 
    teamId, 
    accountId
  );

  const signature = await signBase64(
    getKey(ORIGIN),
    message,
  );
  const headers: { [key: string]: string } = {
    'content-type': 'application/json',
    [eaveHeaders.EAVE_ORIGIN_HEADER]: ORIGIN,
    [eaveHeaders.EAVE_REQUEST_ID_HEADER]: requestId,
    [eaveHeaders.EAVE_SIGNATURE_HEADER]: signature,
  };

  if (accessToken !== undefined) {
    headers[eaveHeaders.EAVE_AUTHORIZATION_HEADER] = `Bearer ${accessToken}`;
  }

  if (teamId !== undefined) {
    headers[eaveHeaders.EAVE_TEAM_ID_HEADER] = teamId;
  }

  if (accountId !== undefined) {
    headers[eaveHeaders.EAVE_ACCOUNT_ID_HEADER] = accountId;
  }

  const requestInit = {
    method,
    body: payload,
    headers,
  };

  console.log('Eave internal API request', {
    'json_fields': {
      'request_id': requestId,
      method,
      url,
    }
  })

  const response = await fetch(url, requestInit);

  console.log(
    'Eave internal API response',
    {
      'json_fields': {
        'request_id': requestId,
        method,
        url,
        'status': response.status,
      }
    },
  )

  if (response.status >= 400) {
    switch (response.status) {
      case 404: throw new NotFoundError(response.statusText);
      case 401: throw new UnauthorizedError(response.statusText);
      case 400: throw new BadRequestError(response.statusText);
      case 500: throw new InternalServerError(response.statusText);
      default: throw new HTTPException(response.status, response.statusText);
    }
  }

  return response;
}
