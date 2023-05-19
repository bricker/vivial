import fetch from 'node-fetch';
import { sharedConfig } from '../config.js';
import * as ops from './operations.js';
import { makeRequest } from '../lib/requests.js';

export async function status(): Promise<ops.Status.ResponseBody> {
  const resp = await fetch(`${sharedConfig.eaveApiBase}/status`, {
    method: 'get',
  });

  const responseData = <ops.Status.ResponseBody>(await resp.json());
  return responseData;
}
export async function upsertDocument(teamId: string, input: ops.UpsertDocument.RequestBody): Promise<ops.UpsertDocument.ResponseBody> {
  const resp = await makeRequest(
    '/documents/upsert',
    input,
    undefined,
    undefined,
    teamId,
  );
  const responseData = <ops.UpsertDocument.ResponseBody>(await resp.json());
  return responseData;
}

export async function createSubscription(teamId: string, input: ops.CreateSubscription.RequestBody): Promise<ops.CreateSubscription.ResponseBody> {
  const resp = await makeRequest(
    '/subscriptions/create',
    input,
    undefined,
    undefined,
    teamId,
  );
  const responseData = <ops.CreateSubscription.ResponseBody>(await resp.json());
  return responseData;
}

export async function deleteSubscription(teamId: string, input: ops.DeleteSubscription.RequestBody): Promise<null> {
  await makeRequest(
    '/subscriptions/delete',
    input,
    undefined,
    undefined,
    teamId,
  );
  return null;
}

export async function getSubscription(teamId: string, input: ops.GetSubscription.RequestBody): Promise<ops.GetSubscription.ResponseBody> {
  const resp = await makeRequest(
    '/subscriptions/query',
    input,
    undefined,
    undefined,
    teamId,
  );
  const responseData = <ops.GetSubscription.ResponseBody>(await resp.json());
  return responseData;
}

export async function getSlackInstallation(input: ops.GetSlackInstallation.RequestBody): Promise<ops.GetSlackInstallation.ResponseBody> {
  const resp = await makeRequest(
    '/installations/slack/query',
    input,
  );
  const responseData = <ops.GetSlackInstallation.ResponseBody>(await resp.json());
  return responseData;
}

export async function getGithubInstallation(input: ops.GetGithubInstallation.RequestBody): Promise<ops.GetGithubInstallation.ResponseBody> {
  const resp = await makeRequest(
    '/installations/github/query',
    input,
  );
  const responseData = <ops.GetGithubInstallation.ResponseBody>(await resp.json());
  return responseData;
}

export async function getTeam(eaveTeamId: string): Promise<ops.GetTeam.ResponseBody> {
  const resp = await makeRequest(
    '/team/query',
    undefined,
    undefined,
    undefined,
    eaveTeamId,
  );
  const responseData = <ops.GetTeam.ResponseBody>(await resp.json());
  return responseData;
}

