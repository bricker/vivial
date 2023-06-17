import { v4 as uuid4 } from 'uuid';
import eaveLogger, { LogContext } from '../logging.js';
import { EaveOrigin } from '../eave-origins.js';
import Signing from '../signing.js';
import eaveHeaders from '../headers.js';
import { redact } from '../util.js';
import { EaveRequestState } from './request-state.js';

const LOG_TAG = 'requests.ts';

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
  ctx?: LogContext;
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

  const ctx = args.ctx || new LogContext();
  ctx.tag = LOG_TAG;

  const requestId = ctx.request_id;
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

  eaveLogger.info({
    message: `Request: ${requestId}: ${method} ${url}`,
    ...ctx,
    ...requestContext,
  });

  const abortController = new AbortController();
  setTimeout(() => abortController.abort(), 1000 * 120);

  const response = await fetch(url, {
    method,
    body: payload,
    headers,
    signal: abortController.signal,
  });

  eaveLogger.info({
    message: `Response: ${requestId}: ${method} ${url}`,
    ...ctx,
    ...requestContext,
    status: response.status,
  });

  if (response.status >= 400) {
    eaveLogger.error({
      ...ctx,
      message: `Request Error (${response.status}): ${url}`,
    });
  }

  return response;
}

export type RequestArgsOrigin = {
  ctx?: LogContext;
  origin: EaveOrigin | string;
}

export type RequestArgsOriginAndTeamId = RequestArgsOrigin & {
  teamId: string;
}
