import { NextFunction, Request, Response } from "express";
import { constants as httpConstants } from "node:http2";
import { ClientRequestParameters } from "./api-types.js";
import { EaveApp } from "./eave-origins.js";
import {
  EAVE_ACCOUNT_ID_HEADER,
  EAVE_ORIGIN_HEADER,
  EAVE_REQUEST_ID_HEADER,
  EAVE_SIGNATURE_HEADER,
  EAVE_SIG_TS_HEADER,
  EAVE_TEAM_ID_HEADER,
  MIME_TYPE_JSON,
} from "./headers.js";
import { LogContext, eaveLogger } from "./logging.js";
import Signing, { buildMessageToSign, makeSigTs } from "./signing.js";
import { JsonObject } from "./types.js";
import { redact } from "./util.js";

export type ExpressHandlerArgs = {
  req: Request;
  res: Response;
  next?: NextFunction;
};

export type CtxArg = {
  ctx: LogContext;
};

export type RequestArgsOrigin = CtxArg & {
  origin: EaveApp | string;
};

export type RequestArgsTeamId = RequestArgsOrigin & {
  teamId: string;
};

export type RequestArgsAuthedRequest = RequestArgsTeamId & {
  accountId: string;
  accessToken: string;
};

type RequestArgs = CtxArg & {
  config: ClientRequestParameters;
  origin: EaveApp | string;
  input?: unknown;
  accountId?: string;
  accessToken?: string;
  teamId?: string;
  method?: string;
  addlHeaders?: { [key: string]: string };
  baseTimeoutSeconds?: number;
};

export async function makeRequest(
  args: RequestArgs,
): Promise<globalThis.Response> {
  const ctx = LogContext.wrap(args.ctx);

  const {
    config,
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
  const eaveSigTs = makeSigTs();
  let payload: string | undefined;

  if (input === undefined) {
    payload = "{}";
  } else if (typeof input !== "string") {
    payload = JSON.stringify(input);
  } else {
    payload = input;
  }

  let headers: { [key: string]: string } = {
    [httpConstants.HTTP2_HEADER_CONTENT_TYPE]: MIME_TYPE_JSON,
    [EAVE_ORIGIN_HEADER]: origin,
    [EAVE_REQUEST_ID_HEADER]: requestId,
    [EAVE_SIG_TS_HEADER]: eaveSigTs.toString(),
  };

  const message = buildMessageToSign({
    method,
    path: config.path,
    ts: eaveSigTs,
    requestId,
    audience: config.audience,
    origin,
    payload,
    teamId,
    accountId,
    ctx,
  });

  const signing = Signing.new(origin);
  const signature = await signing.signBase64(message);

  headers[EAVE_SIGNATURE_HEADER] = signature;

  if (accessToken !== undefined) {
    headers[httpConstants.HTTP2_HEADER_AUTHORIZATION] = `Bearer ${accessToken}`;
  }

  if (teamId !== undefined) {
    headers[EAVE_TEAM_ID_HEADER] = teamId;
  }

  if (accountId !== undefined) {
    headers[EAVE_ACCOUNT_ID_HEADER] = accountId;
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
    url: config.url,
  };

  eaveLogger.info(
    `Client Request: ${requestId}: ${method} ${config.url}`,
    ctx,
    requestContext,
  );

  const abortController = new AbortController();
  setTimeout(() => abortController.abort(), 1000 * baseTimeoutSeconds);

  const response = await fetch(config.url, {
    method,
    body: payload,
    headers,
    signal: abortController.signal,
  });

  eaveLogger.info(
    `Client Response: ${requestId}: ${method} ${config.url}`,
    ctx,
    requestContext,
    { status: response.status },
  );

  if (response.status >= 400) {
    eaveLogger.error(
      `Request Error (${response.status}): ${config.url}`,
      ctx,
      requestContext,
    );
  }

  return response;
}
