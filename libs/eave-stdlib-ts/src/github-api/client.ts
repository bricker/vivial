import * as ops from './operations.js';
import { RequestArgsOriginAndTeamId, makeRequest } from '../requests.js';
import { CreateSubscriptionResponseBody } from '../core-api/operations/subscriptions.js';
import { EaveService } from '../eave-origins.js';
import { sharedConfig } from '../config.js';

const baseUrl = sharedConfig.eaveInternalServiceBase(EaveService.github);

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

export async function createPullRequest(args: RequestArgsOriginAndTeamId & {
  input: ops.CreateGitHubPullRequestRequestBody,
}): Promise<ops.CreateGitHubPullRequestResponseBody> {
  const resp = await makeRequest({
    url: `${baseUrl}/github/api/create-pull-request`,
    ...args,
  });
  const responseData = <ops.CreateGitHubPullRequestResponseBody>(await resp.json());
  return responseData;
}
