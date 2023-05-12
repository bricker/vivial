import { Request, Response } from 'express';
import { GetGithubLinkContent } from '@eave-fyi/eave-stdlib-ts/src/github-api/operations';
import { Subscription } from '@eave-fyi/eave-stdlib-ts/src/core-api/models';

import { App, Octokit } from 'octokit';
import * as superagent from 'superagent';
import { Pair } from '@eave-fyi/eave-stdlib-ts/src/types';
import { GithubRepository } from '@eave-fyi/eave-stdlib-ts/src/github-api/models';
import { appConfig } from '../config.js';

export async function getSummariesAndSubscribe(req: Request, res: Response): Promise<GetGithubLinkContent.ResponseBody> {
  const input = <GetGithubLinkContent.RequestBody>req.body();

}

async function getSummary(): Promise<string> {

}

async function subscribe(): Promise<Subscription> {

}







/**
 * Fetch content of the file located at the URL `url`.
 * @returns null on GitHub API request failure
 */
async function getFileContent(url: string): Promise<string | null> {
  try {
    return getRawContent(url);
  } catch (error) {
    // TODO: logger?
    console.log(error);
    return null;
  }
}

/**
 * Request data about the github repo pointed to by `url` from the GitHub API
 * (`url` doesnt have to point directly to the repo, it can point to any file w/in the repo too)
 */
async function getRepo(client: Octokit, url: string): Promise<GithubRepository> {
  // gather data for API request URL
  const { first: owner, second: repo } = getRepoLocation(url);

  // https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#get-a-repository
  const { data: repository } = await client.rest.repos.get({ owner, repo });
  return <GithubRepository>repository;
}

/**
 * Parse the GitHub org name and repo name from the input `url`
 * @returns Pair(org name, repo name)
 */
function getRepoLocation(url: string): Pair<string, string> {
  // split path from URL
  const urlPathComponents = (new URL(url)).pathname.split('/');

  if (urlPathComponents.length < 3) {
    throw Error(`GitHub URL ${url} did not contain expected org and repo name in its path`);
  }

  // urlPathComponents === ['', 'org', 'repo', ...]
  return { first: urlPathComponents[1]!, second: urlPathComponents[2]! };
}

/**
 * Fetch github file content from `url` using the raw.githubusercontent.com feature
 * Returns null if `url` is not a path to a file (or if some other error was encountered).
 *
 * NOTE: raw.githubusercontent.com is ratelimitted by IP, not requesting user, so this wont scale far
 * https://github.com/github/docs/issues/8031#issuecomment-881427112
 */
async function getRawContent(client: Octokit, url: string): Promise<string | null> {
  const urlComponents = new URL(url);
  // remove blob from URL since raw content URLs dont have it
  const contentLocation = urlComponents.pathname.replace('blob/', '');
  let rawUrl = '';
  // check if enterprise host
  if (!(urlComponents.hostname.match(/github\.com/))) {
    rawUrl = `https://${urlComponents.hostname}/raw`;
  } else {
    rawUrl = 'https://raw.githubusercontent.com';
  }

  const requestUrl = `${rawUrl}${contentLocation}`;

  // get auth token from client
  // auth() documented here https://www.npmjs.com/package/@octokit/auth-token
  const { token: accessToken } = (await client.auth()) as { token: string };

  const result = await superagent.get(requestUrl)
    .set('Authorization', `Bearer ${accessToken}`)
    .set('Accept', 'application/vnd.github.v3.raw');

  const fileContent = result.body as string;
  if (fileContent === '404: Not Found') {
    return null;
  }
  return fileContent;
}

async function createClient(installationId: string): Promise<Octokit> {
  const privateKey = await appConfig.eaveGithubAppPrivateKey;
  const appId = await appConfig.eaveGithubAppId;
  const app = new App({ appId, privateKey });
  const octokit = await app.getInstallationOctokit(parseInt(installationId, 10));
  return octokit;
}
