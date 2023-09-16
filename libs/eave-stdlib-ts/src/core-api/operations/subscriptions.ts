import { sharedConfig } from '../../config.js';
import { EaveApp } from '../../eave-origins.js';
import { CtxArg, RequestArgsOrigin, RequestArgsTeamId, makeRequest } from '../../requests.js';
import { DocumentReference, DocumentReferenceInput, Subscription, SubscriptionInput } from '../models/subscriptions.js';
import { Team } from '../models/team.js';

const baseUrl = sharedConfig.eaveInternalServiceBase(EaveApp.eave_api);

export type GetSubscriptionRequestBody = {
  subscription: SubscriptionInput;
}

export type GetSubscriptionResponseBody = {
  team: Team;
  subscription?: Subscription;
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

export async function createSubscription(args: RequestArgsTeamId & {input: CreateSubscriptionRequestBody}): Promise<CreateSubscriptionResponseBody> {
  const resp = await makeRequest({
    url: `${baseUrl}/subscriptions/create`,
    ...args,
  });
  const responseData = <CreateSubscriptionResponseBody>(await resp.json());
  return responseData;
}

export async function deleteSubscription(args: RequestArgsTeamId & {input: DeleteSubscriptionRequestBody}): Promise<null> {
  await makeRequest({
    url: `${baseUrl}/subscriptions/delete`,
    ...args,
  });
  return null;
}

export async function getSubscription(args: RequestArgsTeamId & {input: GetSubscriptionRequestBody}): Promise<GetSubscriptionResponseBody> {
  const resp = await makeRequest({
    url: `${baseUrl}/subscriptions/query`,
    ...args,
  });
  const responseData = <GetSubscriptionResponseBody>(await resp.json());
  return responseData;
}
