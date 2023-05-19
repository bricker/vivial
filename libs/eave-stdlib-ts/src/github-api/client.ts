import * as ops from './operations';
import { makeRequest } from '../lib/requests.js';
import { sharedConfig } from '../config.js';

export async function createSubscription(
  teamId: string,
  input: ops.CreateGithubResourceSubscription.RequestBody
): Promise<ops.CreateGithubResourceSubscription.ResponseBody> {
  const resp = await makeRequest(
    '/github/api/subscribe',
    input,
    sharedConfig.eaveAppsBase,
    undefined,
    teamId,
  );
  const responseData = <ops.CreateGithubResourceSubscription.ResponseBody>(await resp.json());
  return responseData;
}

export async function getFileContent(
  teamId: string,
  input: ops.GetGithubUrlContent.RequestBody
): Promise<ops.GetGithubUrlContent.ResponseBody> {
  const resp = await makeRequest(
    '/github/api/content',
    input,
    sharedConfig.eaveAppsBase,
    undefined,
    teamId,
  );
  const responseData = <ops.GetGithubUrlContent.ResponseBody>(await resp.json());
  return responseData;
}