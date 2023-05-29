import { v4 as uuid4 } from 'uuid';
import eaveLogger from '../logging.js';
import { EaveOrigin } from '../eave-origins.js';
import { getKey, signBase64 } from '../signing.js';
import eaveHeaders from '../headers.js';
import {
  NotFoundError,
  UnauthorizedError,
  BadRequestError,
  InternalServerError,
  HTTPException,
} from '../exceptions.js';
import { redact } from '../util.js';

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
    method.toUpperCase(),
    url,
    requestId,
    payload,
  ];

  if (teamId !== undefined) {
    signatureElements.push(teamId);
  }
  if (accountId !== undefined) {
    signatureElements.push(accountId);
  }

  return signatureElements.join(':');
}

interface RequestArgs {
  url: string;
  origin: EaveOrigin | string;
  input?: unknown;
  accessToken?: string;
  teamId?: string;
  accountId?: string;
  method?: string;
}

export async function makeRequest(args: RequestArgs): Promise<Response> {
  const {
    url,
    origin,
    input,
    accessToken,
    teamId,
    accountId,
    method = 'post',
  } = args;

  const requestId = uuid4();
  const payload = JSON.stringify(input);
  const message = buildMessageToSign(
    method,
    url,
    requestId,
    origin,
    input === undefined ? '' : JSON.stringify(input),
    teamId,
    accountId,
  );

  const signature = await signBase64(
    getKey(origin),
    message,
  );
  const headers: { [key: string]: string } = {
    'content-type': 'application/json',
    [eaveHeaders.EAVE_ORIGIN_HEADER]: origin,
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

  const requestContext = {
    origin,
    signature: redact(signature),
    access_token: redact(accessToken),
    request_id: requestId,
    team_id: teamId,
    account_id: accountId,
    method,
    url,
  };

  eaveLogger.info(`Eave Client Request: ${requestId}: ${method} ${url}`, requestContext);

  const response = await fetch(url, requestInit);

  eaveLogger.info(`Eave Client Response: ${requestId}: ${method} ${url}`, {
    ...requestContext,
    status: response.status,
  });

  if (response.status >= 400) {
    switch (response.status) {
      case 404: throw new NotFoundError(JSON.stringify(requestContext));
      case 401: throw new UnauthorizedError(JSON.stringify(requestContext));
      case 400: throw new BadRequestError(JSON.stringify(requestContext));
      case 500: throw new InternalServerError(JSON.stringify(requestContext));
      default: throw new HTTPException(response.status, JSON.stringify(requestContext));
    }
  }

  return response;
}

export type RequestArgsOrigin = {
  origin: EaveOrigin | string;
}

export type RequestArgsOriginAndTeamId = RequestArgsOrigin & {
  teamId: string;
}
