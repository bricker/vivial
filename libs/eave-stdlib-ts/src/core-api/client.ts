import { sharedConfig } from '../config';
import * as ops from './operations/operations';
import { RequestArgsOrigin, RequestArgsOriginAndTeamId, makeRequest } from '../lib/requests';

export async function status(): Promise<ops.StatusResponseBody> {
  const resp = await fetch(`${sharedConfig.eaveApiBase}/status`, {
    method: 'get',
  });

  const responseData = <ops.StatusResponseBody>(await resp.json());
  return responseData;
}
export async function upsertDocument({origin,teamId,input}: RequestArgsOriginAndTeamId & {input: ops.UpsertDocumentRequestBody}): Promise<ops.UpsertDocumentResponseBody> {
  const resp = await makeRequest({
    url: `${sharedConfig.eaveApiBase}/documents/upsert`,
    origin,
    input,
    teamId,
  });
  const responseData = <ops.UpsertDocumentResponseBody>(await resp.json());
  return responseData;
}

export async function createSubscription({origin,teamId,input}: RequestArgsOriginAndTeamId & {input: ops.CreateSubscriptionRequestBody}): Promise<ops.CreateSubscriptionResponseBody> {
  const resp = await makeRequest({
    url: `${sharedConfig.eaveApiBase}/subscriptions/create`,
    origin,
    input,
    teamId,
  });
  const responseData = <ops.CreateSubscriptionResponseBody>(await resp.json());
  return responseData;
}

export async function deleteSubscription({origin,teamId,input}: RequestArgsOriginAndTeamId & {input: ops.DeleteSubscriptionRequestBody}): Promise<null> {
  await makeRequest({
    url: `${sharedConfig.eaveApiBase}/subscriptions/delete`,
    origin,
    input,
    teamId,
  });
  return null;
}

export async function getSubscription({origin,teamId,input}: RequestArgsOriginAndTeamId & {input: ops.GetSubscriptionRequestBody}): Promise<ops.GetSubscriptionResponseBody> {
  const resp = await makeRequest({
    url: `${sharedConfig.eaveApiBase}/subscriptions/query`,
    origin,
    input,
    teamId,
  });
  const responseData = <ops.GetSubscriptionResponseBody>(await resp.json());
  return responseData;
}

export async function getSlackInstallation({ origin,input}: RequestArgsOrigin & {input: ops.GetSlackInstallationRequestBody}): Promise<ops.GetSlackInstallationResponseBody> {
  const resp = await makeRequest({
    url: `${sharedConfig.eaveApiBase}/integrations/slack/query`,
    origin,
    input,
  });
  const responseData = <ops.GetSlackInstallationResponseBody>(await resp.json());
  return responseData;
}

export async function getGithubInstallation({origin, input}: RequestArgsOrigin & {input: ops.GetGithubInstallationRequestBody}): Promise<ops.GetGithubInstallationResponseBody> {
  const resp = await makeRequest({
    url: `${sharedConfig.eaveApiBase}/integrations/github/query`,
    origin,
    input,
  });
  const responseData = <ops.GetGithubInstallationResponseBody>(await resp.json());
  return responseData;
}

export async function getTeam({origin,teamId}: RequestArgsOriginAndTeamId): Promise<ops.GetTeamResponseBody> {
  const resp = await makeRequest({
    url: `${sharedConfig.eaveApiBase}/team/query`,
    origin,
    teamId,
  });
  const responseData = <ops.GetTeamResponseBody>(await resp.json());
  return responseData;
}
