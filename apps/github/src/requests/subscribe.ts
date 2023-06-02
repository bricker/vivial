import { Request, Response } from 'express';
import { CreateGithubResourceSubscriptionRequestBody, CreateGithubResourceSubscriptionResponseBody } from '@eave-fyi/eave-stdlib-ts/src/github-api/operations.js';
import { Octokit } from 'octokit';
import { Pair } from '@eave-fyi/eave-stdlib-ts/src/types.js';
import { GithubRepository } from '@eave-fyi/eave-stdlib-ts/src/github-api/models.js';
import headers from '@eave-fyi/eave-stdlib-ts/src/headers.js';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { getEaveState } from '@eave-fyi/eave-stdlib-ts/src/lib/request-state.js';
import { SubscriptionSourceEvent, SubscriptionSourcePlatform } from '@eave-fyi/eave-stdlib-ts/src/core-api/models/subscriptions.js';
import { createSubscription } from '@eave-fyi/eave-stdlib-ts/src/core-api/operations/subscriptions.js';
import { createOctokitClient, getInstallationId } from '../lib/octokit-util.js';
import { appConfig } from '../config.js';

export async function subscribe(req: Request, res: Response): Promise<void> {
  const eaveState = getEaveState(res);

  const eaveTeamId = req.header(headers.EAVE_TEAM_ID_HEADER);
  if (!eaveTeamId) {
    eaveLogger.error('Missing eave-team-id header', eaveState);
    res.status(400).end();
    return;
  }

  const requestBody = (<Buffer>req.body).toString();
  const input = <CreateGithubResourceSubscriptionRequestBody>JSON.parse(requestBody);
  if (!input.url) {
    eaveLogger.error('Missing input.url', eaveState);
    res.status(400).end();
    return;
  }

  let output: CreateGithubResourceSubscriptionResponseBody;

  const instllationId = await getInstallationId(eaveTeamId);
  if (instllationId === null) {
    eaveLogger.error('installation ID not found', eaveState);
    res.status(500).end();
    return;
  }

  // fetch unique info about repo to build subscription source ID
  const client = await createOctokitClient(instllationId);
  const repoInfo = await getRepo(client, input.url);
  const pathChunks = input.url.split(`${repoInfo.full_name}/blob/`);
  // we need the 2nd element, which is branch name + resource path
  if (pathChunks.length < 2) {
    output = { subscription: null };
    res.json(output); // TODO: should we be 400ing or somthing instead of returning null?
  }

  const blobPath = pathChunks[1];
  const sourceId = `${repoInfo.node_id}#${blobPath}`;
  const platform = SubscriptionSourcePlatform.github;
  const event = SubscriptionSourceEvent.github_file_change;

  const subResponse = await createSubscription({
    origin: appConfig.eaveOrigin,
    teamId: eaveTeamId,
    input: {
      subscription: {
        source: {
          platform,
          event,
          id: sourceId,
        },
      },
    },
  });
  output = { subscription: subResponse.subscription };
  res.json(output);
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
