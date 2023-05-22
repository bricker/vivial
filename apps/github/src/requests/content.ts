import { Request, Response } from 'express';
import { Octokit } from 'octokit';
import fetch from 'node-fetch';
import { GetGithubUrlContentRequestBody, GetGithubUrlContentResponseBody } from '@eave-fyi/eave-stdlib-ts/src/github-api/operations.js';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { getEaveState } from '@eave-fyi/eave-stdlib-ts/src/lib/request-state.js';
import headers from '@eave-fyi/eave-stdlib-ts/src/headers.js';
import { getInstallationId, createOctokitClient } from '../lib/octokit-util.js';

export async function getSummary(req: Request, res: Response): Promise<void> {
  const eaveState = getEaveState(res);

  const eaveTeamId = req.header(headers.EAVE_TEAM_ID_HEADER);
  if (!eaveTeamId) {
    eaveLogger.error('Missing eave-team-id header', eaveState);
    res.status(400).end();
    return;
  }

  const requestBody = (<Buffer>req.body).toString();
  const input = <GetGithubUrlContentRequestBody>JSON.parse(requestBody);
  if (!input.url) {
    eaveLogger.error('Invalid input', eaveState);
    res.status(400).end();
    return;
  }

  const installationId = await getInstallationId(eaveTeamId);
  if (installationId === null) {
    eaveLogger.error('missing github installation id', eaveState);
    res.status(500).end();
    return;
  }
  const client = await createOctokitClient(installationId);

  const content = await getFileContent(client, input.url);
  const output: GetGithubUrlContentResponseBody = { content };
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
    eaveLogger.error(error);
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

  const result = await fetch(
    requestUrl, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${accessToken}`,
        Accept: 'application/vnd.github.v3.raw',
      },
    },
  );

  const fileContent = <string> await result.json();
  if (fileContent === '404: Not Found') {
    eaveLogger.warning(`file not found: ${requestUrl}`);
    return null;
  }
  return fileContent;
}
