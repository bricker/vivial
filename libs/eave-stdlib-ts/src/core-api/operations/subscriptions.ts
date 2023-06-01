import { sharedConfig } from '../../config.js';
import { RequestArgsOriginAndTeamId, makeRequest } from '../../lib/requests.js';
import { DocumentReference, DocumentReferenceInput, Subscription, SubscriptionInput } from '../models/subscriptions.js';
import { Team } from '../models/team.js';


export type GetSubscriptionRequestBody = {
  subscription: SubscriptionInput;
}

export type GetSubscriptionResponseBody = {
  team: Team;
  subscription: Subscription;
  document_reference?: DocumentReference;
}

export type CreateSubscriptionRequestBody = {
  subscription: SubscriptionInput;
  document_reference?: DocumentReferenceInput;
}

export type CreateSubscriptionResponseBody = {
  team: Team;
  subscription: Subscription;
  document_reference?: DocumentReference;
}

export type DeleteSubscriptionRequestBody = {
  subscription: SubscriptionInput;
}

export async function createSubscription({ origin, teamId, input }: RequestArgsOriginAndTeamId & {input: CreateSubscriptionRequestBody}): Promise<CreateSubscriptionResponseBody> {
  const resp = await makeRequest({
    url: `${sharedConfig.eaveApiBase}/subscriptions/create`,
    origin,
    input,
    teamId,
  });
  const responseData = <CreateSubscriptionResponseBody>(await resp.json());
  return responseData;
}

export async function deleteSubscription({ origin, teamId, input }: RequestArgsOriginAndTeamId & {input: DeleteSubscriptionRequestBody}): Promise<null> {
  await makeRequest({
    url: `${sharedConfig.eaveApiBase}/subscriptions/delete`,
    origin,
    input,
    teamId,
  });
  return null;
}

export async function getSubscription({ origin, teamId, input }: RequestArgsOriginAndTeamId & {input: GetSubscriptionRequestBody}): Promise<GetSubscriptionResponseBody> {
  const resp = await makeRequest({
    url: `${sharedConfig.eaveApiBase}/subscriptions/query`,
    origin,
    input,
    teamId,
  });
  const responseData = <GetSubscriptionResponseBody>(await resp.json());
  return responseData;
}
