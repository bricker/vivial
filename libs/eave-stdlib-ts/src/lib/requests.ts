import { v4 as uuid4 } from 'uuid';
import eaveLogger from '../logging.js';
import { EaveOrigin } from '../eave-origins.js';
import Signing from '../signing.js';
import eaveHeaders from '../headers.js';
import {
  NotFoundError,
  UnauthorizedError,
  BadRequestError,
  InternalServerError,
  HTTPException,
} from '../exceptions.js';
import { redact } from '../util.js';

export function buildMessageToSign({
  method,
  url,
  requestId,
  origin,
  payload,
  teamId,
  accountId,
}: {
  method: string,
  url: string,
  requestId: string,
  origin: EaveOrigin | string,
  payload: string,
  teamId?: string,
  accountId?: string,
}): string {
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
  sign?: boolean;
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
  const payload = input === undefined ? '{}' : JSON.stringify(input);

  const headers: { [key: string]: string } = {
    'content-type': 'application/json',
    [eaveHeaders.EAVE_ORIGIN_HEADER]: origin,
    [eaveHeaders.EAVE_REQUEST_ID_HEADER]: requestId,
  };

  const message = buildMessageToSign({
    method,
    url,
    requestId,
    origin,
    payload,
    teamId,
    accountId,
  });

  const signing = Signing.new(origin);
  const signature = await signing.signBase64(message);

  headers[eaveHeaders.EAVE_SIGNATURE_HEADER] = signature;

  if (accessToken !== undefined) {
    headers[eaveHeaders.EAVE_AUTHORIZATION_HEADER] = `Bearer ${accessToken}`;
  }

  if (teamId !== undefined) {
    headers[eaveHeaders.EAVE_TEAM_ID_HEADER] = teamId;
  }

  if (accountId !== undefined) {
    headers[eaveHeaders.EAVE_ACCOUNT_ID_HEADER] = accountId;
  }

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

  eaveLogger.info({ message: `Eave Client Request: ${requestId}: ${method} ${url}`, eaveState: requestContext });

  const abortController = new AbortController();
  setTimeout(() => abortController.abort(), 1000 * 10); // Abort after 10 seconds

  const response = await fetch(url, {
    method,
    body: payload,
    headers,
    signal: abortController.signal,
  });

  eaveLogger.info({
    message: `Eave Client Response: ${requestId}: ${method} ${url}`,
    eaveState: {
      ...requestContext,
      status: response.status,
    },
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
