import fetch from 'node-fetch';
import { sharedConfig } from '../config.js';
import * as ops from './operations.js';
import { makeRequest } from '../lib/requests.js';

export async function status(): Promise<ops.StatusResponseBody> {
  const resp = await fetch(`${sharedConfig.eaveApiBase}/status`, {
    method: 'get',
  });

  const responseData = <ops.StatusResponseBody>(await resp.json());
  return responseData;
}
export async function upsertDocument(teamId: string, input: ops.UpsertDocumentRequestBody): Promise<ops.UpsertDocumentResponseBody> {
  const resp = await makeRequest(
    '/documents/upsert',
    input,
    undefined,
    undefined,
    teamId,
  );
  const responseData = <ops.UpsertDocumentResponseBody>(await resp.json());
  return responseData;
}

export async function createSubscription(teamId: string, input: ops.CreateSubscriptionRequestBody): Promise<ops.CreateSubscriptionResponseBody> {
  const resp = await makeRequest(
    '/subscriptions/create',
    input,
    undefined,
    undefined,
    teamId,
  );
  const responseData = <ops.CreateSubscriptionResponseBody>(await resp.json());
  return responseData;
}

export async function deleteSubscription(teamId: string, input: ops.DeleteSubscriptionRequestBody): Promise<null> {
  await makeRequest(
    '/subscriptions/delete',
    input,
    undefined,
    undefined,
    teamId,
  );
  return null;
}

export async function getSubscription(teamId: string, input: ops.GetSubscriptionRequestBody): Promise<ops.GetSubscriptionResponseBody> {
  const resp = await makeRequest(
    '/subscriptions/query',
    input,
    undefined,
    undefined,
    teamId,
  );
  const responseData = <ops.GetSubscriptionResponseBody>(await resp.json());
  return responseData;
}

export async function getSlackInstallation(input: ops.GetSlackInstallationRequestBody): Promise<ops.GetSlackInstallationResponseBody> {
  const resp = await makeRequest(
    '/installations/slack/query',
    input,
  );
  const responseData = <ops.GetSlackInstallationResponseBody>(await resp.json());
  return responseData;
}

export async function getGithubInstallation(input: ops.GetGithubInstallationRequestBody): Promise<ops.GetGithubInstallationResponseBody> {
  const resp = await makeRequest(
    '/installations/github/query',
    input,
  );
  const responseData = <ops.GetGithubInstallationResponseBody>(await resp.json());
  return responseData;
}

export async function getTeam(eaveTeamId: string): Promise<ops.GetTeamResponseBody> {
  const resp = await makeRequest(
    '/team/query',
    undefined,
    undefined,
    undefined,
    eaveTeamId,
  );
  const responseData = <ops.GetTeamResponseBody>(await resp.json());
  return responseData;
}
