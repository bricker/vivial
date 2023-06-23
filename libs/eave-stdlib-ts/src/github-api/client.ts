import * as ops from './operations.js';
import { RequestArgsOriginAndTeamId, makeRequest } from '../requests.js';
import { sharedConfig } from '../config.js';

export async function createSubscription(args: RequestArgsOriginAndTeamId & {
  input: ops.CreateGithubResourceSubscriptionRequestBody,
}): Promise<ops.CreateGithubResourceSubscriptionResponseBody> {
  const resp = await makeRequest({
    url: `${sharedConfig.eaveAppsBase}/github/api/subscribe`,
    ...args,
  });
  const responseData = <ops.CreateGithubResourceSubscriptionResponseBody>(await resp.json());
  return responseData;
}

export async function getFileContent(args: RequestArgsOriginAndTeamId & {
  input: ops.GetGithubUrlContentRequestBody,
}): Promise<ops.GetGithubUrlContentResponseBody> {
  const resp = await makeRequest({
    url: `${sharedConfig.eaveAppsBase}/github/api/content`,
    ...args,
  });
  const responseData = <ops.GetGithubUrlContentResponseBody>(await resp.json());
  return responseData;
}
