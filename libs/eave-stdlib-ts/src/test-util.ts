import { createHash } from "crypto";
import express from "express";
import { v4 as uuidv4 } from "uuid";
import { EaveApp } from "./eave-origins.js";
import { InvalidSignatureError } from "./exceptions.js";
import { LogContext } from "./logging.js";
import Signing, { buildMessageToSign, makeSigTs } from "./signing.js";

/*
  These libraries aren't listed in the dependencies for eave-stdlib-ts, because they are development dependencies but this file is exported from this library.
  So when this file is imported, they need to be available from somewhere else (probably the app or repo running the tests).
  These imports will fail in a non-development environment.
*/
/* eslint-disable import/order, import/no-extraneous-dependencies */
import sinon from "sinon";
import request from "supertest";
/* eslint-enable import/order, import/no-extraneous-dependencies */

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

function fakeSign(m: string | Buffer): string {
  return createHash("sha256").update(m).digest().toString("base64");
}

const replacementSignFunc = async (data: string | Buffer): Promise<string> => {
  return fakeSign(data);
};

const replacementVerifyFunc = async (message: string | Buffer, signature: string | Buffer): Promise<void> => {
  const expected = fakeSign(message);

  if (signature.toString("base64") !== expected) {
    throw new InvalidSignatureError("Signature failed verification");
  }
};

export function mockSigning({ sandbox }: { sandbox: sinon.SinonSandbox }) {
  const mock = new Signing("eave_www");
  sandbox.stub(Signing, "new").returns(mock);
  sandbox.stub(mock, "signBase64").callsFake(replacementSignFunc);
  sandbox.stub(mock, "verifySignatureOrException").callsFake(replacementVerifyFunc);
}

export async function makeRequest({ app, path, teamId, accountId, input, accessToken, headers, audience, method = "post", origin = EaveApp.eave_www, requestId = uuidv4() }: { app: express.Express; path: string; audience: EaveApp; input?: unknown; method?: "get" | "post"; origin?: EaveApp; teamId?: string; accountId?: string; accessToken?: string; requestId?: string; headers?: { [key: string]: string } }): Promise<request.Test> {
  const ctx = new LogContext();
  const updatedHeaders: { [key: string]: string } = {};
  const requestAgent = request(app)[method](path).type("json");

  if (teamId !== undefined) {
    updatedHeaders["eave-team-id"] = teamId;
  }
  if (origin !== undefined) {
    updatedHeaders["eave-origin"] = origin;
  }
  if (accountId !== undefined) {
    updatedHeaders["eave-account-id"] = accountId;
  }

  if (accessToken !== undefined) {
    updatedHeaders["authorization"] = `Bearer ${accessToken}`;
  }

  let eaveSigTs: number;
  const eaveSigTsHeader = headers?.["eave-sig-ts"];
  if (eaveSigTsHeader) {
    eaveSigTs = parseInt(eaveSigTsHeader, 10);
  } else {
    eaveSigTs = makeSigTs();
    updatedHeaders["eave-sig-ts"] = eaveSigTs.toString();
  }

  updatedHeaders["eave-request-id"] = requestId;
  updatedHeaders["eave-origin"] = origin;

  let encodedPayload: string;

  if (input === undefined) {
    encodedPayload = "{}";
  } else if (typeof input !== "string") {
    encodedPayload = JSON.stringify(input);
  } else {
    encodedPayload = input;
  }

  const message = buildMessageToSign({
    method,
    path,
    ts: eaveSigTs,
    requestId,
    origin,
    audience,
    payload: encodedPayload,
    teamId,
    accountId,
    ctx,
  });

  const signing = Signing.new(origin);
  const signature = await signing.signBase64(message);
  updatedHeaders["eave-signature"] = signature;

  if (headers !== undefined) {
    Object.assign(updatedHeaders, headers);
  }

  const response = await requestAgent.set(updatedHeaders).send(encodedPayload);

  return response;
}
