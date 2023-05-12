import fetch from 'node-fetch';
import * as ops from './operations';
import { initRequest } from '../lib/requests.js';
import { sharedConfig } from '../config.js';

export async function createSubscription(
  teamId: string,
  input: ops.CreateGithubResourceSubscription.RequestBody
): Promise<ops.CreateGithubResourceSubscription.ResponseBody> {
  const request = await initRequest(input, teamId);
  const resp = await fetch(`${sharedConfig.eaveApiBase}/github/subscribe`, request);

  const responseData = <ops.CreateGithubResourceSubscription.ResponseBody>(await resp.json());
  return responseData;
}

export async function getFileContent(
  teamId: string,
  input: ops.GetGithubUrlContent.RequestBody
): Promise<ops.GetGithubUrlContent.ResponseBody> {
  const request = await initRequest(input, teamId);
  const resp = await fetch(`${sharedConfig.eaveApiBase}/github/content`, request);

  const responseData = <ops.GetGithubUrlContent.ResponseBody>(await resp.json());
  return responseData;
}