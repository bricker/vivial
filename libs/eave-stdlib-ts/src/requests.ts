import { NextFunction, Request, Response } from "express";
import { constants as httpConstants } from "node:http2";
import { ApiEndpointClientConfiguration } from "./api-util.js";
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

export type RequestArgsAuthedRequest = RequestArgsOrigin & {
  accountId: string;
  accessToken: string;
};

type RequestArgs = CtxArg & {
  config: ApiEndpointClientConfiguration;
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
    accountId = ctx?.eave_account_id,
    method = httpConstants.HTTP2_METHOD_POST,
    baseTimeoutSeconds = 600,
  } = args;

  const requestId = ctx.eave_request_id;
  let payload: string | undefined;

  if (input === undefined) {
    payload = "{}";
  } else if (typeof input !== "string") {
    payload = JSON.stringify(input);
  } else {
    payload = input;
  }

  const requestContext: JsonObject = {
    eave_origin: origin,
    eave_request_id: requestId,
    method,
    url: config.url,
  };

  let headers: { [key: string]: string } = {
    [httpConstants.HTTP2_HEADER_CONTENT_TYPE]: MIME_TYPE_JSON,
    [EAVE_ORIGIN_HEADER]: origin,
    [EAVE_REQUEST_ID_HEADER]: requestId,
  };

  if (config.authRequired) {
    if (accessToken === undefined) {
      throw new Error("missing access_token");
    }
    headers[httpConstants.HTTP2_HEADER_AUTHORIZATION] = `Bearer ${accessToken}`;
    requestContext["access_token"] = redact(accessToken);

    if (accountId === undefined) {
      throw new Error("missing account_id");
    }
    headers[EAVE_ACCOUNT_ID_HEADER] = accountId;
    requestContext["eave_account_id"] = accountId;
  }

  if (addlHeaders) {
    headers = Object.assign(headers, addlHeaders);
  }

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
