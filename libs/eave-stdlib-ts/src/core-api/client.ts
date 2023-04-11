import fetch, { RequestInit } from 'node-fetch';
import { sharedConfig } from '../config';
import * as ops from './operations';
import { computeSignature } from './signing';

export async function status(): Promise<ops.Status.ResponseBody> {
  const resp = await fetch(`${sharedConfig.eaveApiBase}/status`, {
    method: 'get',
  });

  const responseData = <ops.Status.ResponseBody>(await resp.json());
  return responseData;
}
export async function upsertDocument(teamId: string, input: ops.UpsertDocument.RequestBody): Promise<ops.UpsertDocument.ResponseBody> {
  const request = await initRequest(input, teamId);
  const resp = await fetch(`${sharedConfig.eaveApiBase}/documents/upsert`, request);

  const responseData = <ops.UpsertDocument.ResponseBody>(await resp.json());
  return responseData;
}

export async function createSubscription(teamId: string, input: ops.CreateSubscription.RequestBody): Promise<ops.CreateSubscription.ResponseBody> {
  const request = await initRequest(input, teamId);
  const resp = await fetch(`${sharedConfig.eaveApiBase}/subscriptions/create`, request);

  const responseData = <ops.CreateSubscription.ResponseBody>(await resp.json());
  return responseData;
}

export async function getSubscription(teamId: string, input: ops.GetSubscription.RequestBody): Promise<ops.GetSubscription.ResponseBody | null> {
  const request = await initRequest(input, teamId);
  const resp = await fetch(`${sharedConfig.eaveApiBase}/subscriptions/query`, request);

  if (resp.status >= 300) {
    return null;
  }

  const responseData = <ops.GetSubscription.ResponseBody>(await resp.json());
  return responseData;
}


async function getSlackSource(input: ops.GetSlackSource.RequestBody): Promise<ops.GetSlackSource.ResponseBody | null> {
  const request = await initRequest(input);
  const resp = await fetch(`${sharedConfig.eaveApiBase}/slack_sources/query`, request);


  if (resp.status >= 300) {
    return null;
  }

  const responseData = <ops.GetSlackSource.ResponseBody>(await resp.json());
  return responseData;
}

async function initRequest(data: unknown, teamId?: string): Promise<RequestInit> {
  const payload = JSON.stringify(data);
  const signature = await computeSignature(payload, teamId);
  const headers = {
    'content-type': 'application/json',
    'eave-signature': signature,
  };

  if (teamId !== undefined) {
    headers['eave-team-id'] = teamId;
  }

  return {
    method: 'post',
    body: payload,
    headers,
  };
}
