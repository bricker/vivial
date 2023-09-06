import * as ops from './operations.js';
import { RequestArgsOriginAndTeamId, makeRequest } from '../requests.js';
import { CreateSubscriptionResponseBody } from '../core-api/operations/subscriptions.js';
import { EaveApp } from '../eave-origins.js';
import { sharedConfig } from '../config.js';

const baseUrl = sharedConfig.eaveInternalServiceBase(EaveApp.eave_github_app);

export async function createSubscription(args: RequestArgsOriginAndTeamId & {
  input: ops.CreateGithubResourceSubscriptionRequestBody,
}): Promise<CreateSubscriptionResponseBody> {
  const resp = await makeRequest({
    url: `${baseUrl}/github/api/subscribe`,
    ...args,
  });
  const responseData = <CreateSubscriptionResponseBody>(await resp.json());
  return responseData;
}

export async function getFileContent(args: RequestArgsOriginAndTeamId & {
  input: ops.GetGithubUrlContentRequestBody,
}): Promise<ops.GetGithubUrlContentResponseBody> {
  const resp = await makeRequest({
    url: `${baseUrl}/github/api/content`,
    ...args,
  });
  const responseData = <ops.GetGithubUrlContentResponseBody>(await resp.json());
  return responseData;
}
