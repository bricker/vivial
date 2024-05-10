import express from "express";
import { constants as httpConstants } from "node:http2";
import { v4 as uuidv4 } from "uuid";
import { EaveApp } from "./eave-origins.js";

/*
  These libraries aren't listed in the dependencies for eave-stdlib-ts, because they are development dependencies but this file is exported from this library.
  So when this file is imported, they need to be available from somewhere else (probably the app or repo running the tests).
  These imports will fail in a non-development environment.
*/
import request from "supertest";
import {
  EAVE_ACCOUNT_ID_HEADER,
  EAVE_ORIGIN_HEADER,
  EAVE_REQUEST_ID_HEADER,
  EAVE_TEAM_ID_HEADER,
} from "./headers.js";

export class TestUtil {
  testData: { [key: string]: any } = {};

  anyint(name?: string): number {
    name = name || uuidv4();

    if (this.testData[name] === undefined) {
      this.testData[name] = Math.trunc(Math.random() * Math.pow(10, 5));
    }

    return this.testData[name];
  }

  getint(name: string): number {
    return this.testData[name];
  }

  anystr(name?: string): string {
    name = name || uuidv4();

    if (this.testData[name] === undefined) {
      this.testData[name] = uuidv4();
    }

    return this.testData[name];
  }

  getstr(name: string): string {
    return this.testData[name];
  }
}

export interface TestContextBase {
  u: TestUtil;
}

export async function makeRequest({
  app,
  path,
  teamId,
  accountId,
  input,
  accessToken,
  headers,
  method = "post",
  origin = EaveApp.eave_dashboard,
  requestId = uuidv4(),
}: {
  app: express.Express;
  path: string;
  input?: unknown;
  method?: "get" | "post";
  origin?: EaveApp;
  teamId?: string;
  accountId?: string;
  accessToken?: string;
  requestId?: string;
  headers?: { [key: string]: string };
}): Promise<request.Test> {
  const updatedHeaders: { [key: string]: string } = {};
  const requestAgent = request(app)[method](path).type("json");

  if (teamId !== undefined) {
    updatedHeaders[EAVE_TEAM_ID_HEADER] = teamId;
  }
  if (origin !== undefined) {
    updatedHeaders[EAVE_ORIGIN_HEADER] = origin;
  }
  if (accountId !== undefined) {
    updatedHeaders[EAVE_ACCOUNT_ID_HEADER] = accountId;
  }

  if (accessToken !== undefined) {
    updatedHeaders[
      httpConstants.HTTP2_HEADER_AUTHORIZATION
    ] = `Bearer ${accessToken}`;
  }

  updatedHeaders[EAVE_REQUEST_ID_HEADER] = requestId;
  updatedHeaders[EAVE_ORIGIN_HEADER] = origin;

  let encodedPayload: string;

  if (input === undefined) {
    encodedPayload = "{}";
  } else if (typeof input !== "string") {
    encodedPayload = JSON.stringify(input);
  } else {
    encodedPayload = input;
  }

  if (headers !== undefined) {
    Object.assign(updatedHeaders, headers);
  }

  const response = await requestAgent.set(updatedHeaders).send(encodedPayload);

  return response;
}
