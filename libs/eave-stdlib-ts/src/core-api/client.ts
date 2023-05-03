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

export async function deleteSubscription(teamId: string, input: ops.DeleteSubscription.RequestBody): Promise<null> {
  const request = await initRequest(input, teamId);
  await fetch(`${sharedConfig.eaveApiBase}/subscriptions/delete`, request);
  return null;
}

export async function getSubscription(teamId: string, input: ops.GetSubscription.RequestBody): Promise<ops.GetSubscription.ResponseBody> {
  const request = await initRequest(input, teamId);
  const resp = await fetch(`${sharedConfig.eaveApiBase}/subscriptions/query`, request);

  const responseData = <ops.GetSubscription.ResponseBody>(await resp.json());
  return responseData;
}

export async function getSlackInstallation(input: ops.GetSlackInstallation.RequestBody): Promise<ops.GetSlackInstallation.ResponseBody> {
  const request = await initRequest(input);
  const resp = await fetch(`${sharedConfig.eaveApiBase}/installations/slack/query`, request);

  const responseData = <ops.GetSlackInstallation.ResponseBody>(await resp.json());
  return responseData;
}

export async function getGithubInstallation(input: ops.GetGithubInstallation.RequestBody): Promise<ops.GetGithubInstallation.ResponseBody> {
  const request = await initRequest(input);
  const resp = await fetch(`${sharedConfig.eaveApiBase}/installations/github/query`, request);

  const responseData = <ops.GetGithubInstallation.ResponseBody>(await resp.json());
  return responseData;
}

export async function getTeam(eaveTeamId: string): Promise<ops.GetTeam.ResponseBody> {
  const request = await initRequest(undefined, eaveTeamId);
  const resp = await fetch(`${sharedConfig.eaveApiBase}/team/query`, request);

  const responseData = <ops.GetTeam.ResponseBody>(await resp.json());
  return responseData;
}

async function initRequest(data: unknown, teamId?: string): Promise<RequestInit> {
  const payload = JSON.stringify(data);
  const signature = await computeSignature(payload, teamId);
  const headers: { [key: string]: string } = {
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
