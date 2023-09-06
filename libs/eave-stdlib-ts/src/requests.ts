import { constants as httpConstants } from 'node:http2';
import { NextFunction, Request, Response } from 'express';
import eaveLogger, { LogContext } from './logging.js';
import { EaveApp } from './eave-origins.js';
import Signing, { buildMessageToSign } from './signing.js';
import eaveHeaders from './headers.js';
import { redact } from './util.js';
import { JsonObject } from './types.js';

export type ExpressHandlerArgs = {
  req: Request;
  res: Response;
  next?: NextFunction;
}

export type CtxArg = {
  ctx?: LogContext;
}

export type RequestArgsOrigin = CtxArg & {
  origin: EaveApp | string;
}

export type RequestArgsOriginAndTeamId = RequestArgsOrigin & {
  teamId: string;
}

type RequestArgs = CtxArg & {
  url: string;
  origin: EaveApp | string;
  input?: unknown;
  accessToken?: string;
  teamId?: string;
  accountId?: string;
  method?: string;
  ctx?: LogContext;
  addlHeaders?: {[key:string]: string};
  baseTimeoutSeconds?: number;
}

export async function makeRequest(args: RequestArgs): Promise<globalThis.Response> {
  const ctx = LogContext.wrap(args.ctx);

  const {
    url,
    origin,
    input,
    accessToken,
    addlHeaders,
    teamId = ctx?.eave_team_id,
    accountId = ctx?.eave_account_id,
    method = httpConstants.HTTP2_METHOD_POST,
    baseTimeoutSeconds = 600,
  } = args;

  const requestId = ctx.eave_request_id;
  let payload: string | undefined;

  if (input === undefined) {
    payload = '{}';
  } else if (typeof input !== 'string') {
    payload = JSON.stringify(input);
  } else {
    payload = input;
  }

  let headers: { [key: string]: string } = {
    [httpConstants.HTTP2_HEADER_CONTENT_TYPE]: eaveHeaders.MIME_TYPE_JSON,
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
    ctx,
  });

  const signing = Signing.new(origin);
  const signature = await signing.signBase64(message);

  headers[eaveHeaders.EAVE_SIGNATURE_HEADER] = signature;

  if (accessToken !== undefined) {
    headers[httpConstants.HTTP2_HEADER_AUTHORIZATION] = `Bearer ${accessToken}`;
  }

  if (teamId !== undefined) {
    headers[eaveHeaders.EAVE_TEAM_ID_HEADER] = teamId;
  }

  if (accountId !== undefined) {
    headers[eaveHeaders.EAVE_ACCOUNT_ID_HEADER] = accountId;
  }

  if (addlHeaders) {
    headers = Object.assign(headers, addlHeaders);
  }

  const requestContext: JsonObject = {
    eave_origin: origin,
    signature: redact(signature),
    access_token: redact(accessToken),
    eave_request_id: requestId,
    eave_team_id: teamId,
    eave_account_id: accountId,
    method,
    url,
  };

  eaveLogger.info(
    `Client Request: ${requestId}: ${method} ${url}`,
    ctx,
    requestContext,
  );

  const abortController = new AbortController();
  setTimeout(() => abortController.abort(), 1000 * baseTimeoutSeconds);

  try {
    const response = await fetch(url, {
      method,
      body: payload,
      headers,
      signal: abortController.signal,
    });

    eaveLogger.info(
      `Client Response: ${requestId}: ${method} ${url}`,
      ctx,
      requestContext,
      { status: response.status },
    );

    if (response.status >= 400) {
      eaveLogger.error(
        `Request Error (${response.status}): ${url}`,
        ctx,
        requestContext,
      );
    }

    return response;
  } catch (e: unknown) {
    // TODO: Remove this block, it was just for debugging
    console.log(e);
    throw e;
  }
}
