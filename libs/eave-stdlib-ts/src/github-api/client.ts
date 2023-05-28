import * as ops from './operations';
import { RequestArgsOriginAndTeamId, makeRequest } from '../lib/requests';
import { sharedConfig } from '../config';

export async function createSubscription({ origin, teamId, input }: RequestArgsOriginAndTeamId & {
  input: ops.CreateGithubResourceSubscriptionRequestBody,
}): Promise<ops.CreateGithubResourceSubscriptionResponseBody> {
  const resp = await makeRequest({
    origin,
    url: `${sharedConfig.eaveAppsBase}/github/api/subscribe`,
    input,
    teamId,
  });
  const responseData = <ops.CreateGithubResourceSubscriptionResponseBody>(await resp.json());
  return responseData;
}

export async function getFileContent({ origin, teamId, input }: RequestArgsOriginAndTeamId & {
  input: ops.GetGithubUrlContentRequestBody,
}): Promise<ops.GetGithubUrlContentResponseBody> {
  const resp = await makeRequest({
    origin,
    url: `${sharedConfig.eaveAppsBase}/github/api/content`,
    input,
    teamId,
  });
  const responseData = <ops.GetGithubUrlContentResponseBody>(await resp.json());
  return responseData;
}
