import * as ops from './operations.js';
import { RequestArgsOriginAndTeamId, appengineBaseUrl, makeRequest } from '../requests.js';
import { CreateSubscriptionResponseBody } from '../core-api/operations/subscriptions.js';
import { EaveService } from '../eave-origins.js';

const baseUrl = appengineBaseUrl(EaveService.github);

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
