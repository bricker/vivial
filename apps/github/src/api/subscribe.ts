import {
  SubscriptionSourceEvent,
  SubscriptionSourcePlatform,
} from "@eave-fyi/eave-stdlib-ts/src/core-api/models/subscriptions.js";
import { CreateSubscriptionOperation } from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/subscriptions.js";
import { GithubRepository } from "@eave-fyi/eave-stdlib-ts/src/github-api/models.js";
import { CreateGithubResourceSubscriptionRequestBody } from "@eave-fyi/eave-stdlib-ts/src/github-api/operations/create-subscription.js";
import { EAVE_TEAM_ID_HEADER } from "@eave-fyi/eave-stdlib-ts/src/headers.js";
import {
  LogContext,
  eaveLogger,
} from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import { Pair } from "@eave-fyi/eave-stdlib-ts/src/types.js";
import { assertPresence } from "@eave-fyi/eave-stdlib-ts/src/util.js";
import { Request, Response } from "express";
import { Octokit } from "octokit";
import { appConfig } from "../config.js";
import { createTeamOctokitClient } from "../lib/octokit-util.js";

export async function subscribeHandler(
  req: Request,
  res: Response,
): Promise<void> {
  const ctx = LogContext.load(res);
  const octokit = await createTeamOctokitClient(req, ctx);
  const eaveTeamId = req.header(EAVE_TEAM_ID_HEADER);
  assertPresence(eaveTeamId);

  const input = <CreateGithubResourceSubscriptionRequestBody>req.body;
  if (!input.url) {
    eaveLogger.error("Missing input.url", ctx);
    res.sendStatus(400);
    return;
  }

  // fetch unique info about repo to build subscription source ID
  const repoInfo = await getRepo(octokit, input.url);
  const pathChunks = input.url.split(`${repoInfo.full_name}/blob/`);
  // we need the 2nd element, which is branch name + resource path
  if (pathChunks.length < 2) {
    res.sendStatus(400);
    return;
  }

  const blobPath = pathChunks[1];
  const sourceId = `${repoInfo.node_id}#${blobPath}`;
  const platform = SubscriptionSourcePlatform.github;
  const event = SubscriptionSourceEvent.github_file_change;

  const subResponse = await CreateSubscriptionOperation.perform({
    ctx,
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
  res.json(subResponse);
}

/**
 * Request data about the github repo pointed to by `url` from the GitHub API
 * (`url` doesnt have to point directly to the repo, it can point to any file w/in the repo too)
 */
async function getRepo(
  client: Octokit,
  url: string,
): Promise<GithubRepository> {
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
  const urlPathComponents = new URL(url).pathname.split("/");

  if (urlPathComponents.length < 3) {
    throw Error(
      `GitHub URL ${url} did not contain expected org and repo name in its path`,
    );
  }

  // urlPathComponents === ['', 'org', 'repo', ...]
  return { first: urlPathComponents[1]!, second: urlPathComponents[2]! };
}
