import { Request, Response } from 'express';
import { GetGithubUrlContent } from '@eave-fyi/eave-stdlib-ts/src/github-api/operations.js';
import { Octokit } from 'octokit';
import * as superagent from 'superagent';
import { getInstallationId, createOctokitClient } from '../lib/octokit-util.js';

export async function getSummary(req: Request, res: Response): Promise<void> {
  const input = <GetGithubUrlContent.RequestBody>req.body;
  if (!(input.url)) {
    res.status(400).end();
    return;
  }

  const installationId = await getInstallationId(input.eaveTeamId);
  if (installationId === null) {
    res.status(500).end();
    return;
  }
  const client = await createOctokitClient(installationId);

  const content = await getFileContent(client, input.url);
  const output: GetGithubUrlContent.ResponseBody = { content };
  res.json(output);
}

/**
 * Fetch content of the file located at the URL `url`.
 * @returns null on GitHub API request failure
 */
async function getFileContent(client: Octokit, url: string): Promise<string | null> {
  try {
    return getRawContent(client, url);
  } catch (error) {
    // TODO: logger?
    console.log(error);
    return null;
  }
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
