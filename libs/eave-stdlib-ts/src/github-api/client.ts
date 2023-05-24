import * as ops from './operations.js';
import { makeRequest } from '../lib/requests.js';
import { sharedConfig } from '../config.js';

export async function createSubscription(
  teamId: string,
  input: ops.CreateGithubResourceSubscriptionRequestBody,
): Promise<ops.CreateGithubResourceSubscriptionResponseBody> {
  const resp = await makeRequest({
    url: `${sharedConfig.eaveAppsBase}/github/api/subscribe`,
    input,
    teamId,
  });
  const responseData = <ops.CreateGithubResourceSubscriptionResponseBody>(await resp.json());
  return responseData;
}

export async function getFileContent(
  teamId: string,
  input: ops.GetGithubUrlContentRequestBody,
): Promise<ops.GetGithubUrlContentResponseBody> {
  const resp = await makeRequest({
    url: `${sharedConfig.eaveAppsBase}/github/api/content`,
    input,
    teamId,
  });
  const responseData = <ops.GetGithubUrlContentResponseBody>(await resp.json());
  return responseData;
}
