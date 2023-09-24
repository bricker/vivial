import { ExternalGithubRepo } from "@eave-fyi/eave-stdlib-ts/src/github-api/models.js";
import { QueryGithubReposResponseBody } from "@eave-fyi/eave-stdlib-ts/src/github-api/operations/query-repos.js";
import { LogContext } from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import { Query, Repository } from "@octokit/graphql-schema";
import assert from "assert";
import { Request, Response } from "express";
import { loadQuery } from "../lib/graphql-util.js";
import { createTeamOctokitClient } from "../lib/octokit-util.js";

export async function queryReposHandler(req: Request, res: Response): Promise<void> {
  const ctx = LogContext.load(res);
  const octokit = await createTeamOctokitClient(req, ctx);

  const query = await loadQuery("getRepos");
  const response = await octokit.graphql<{ viewer: Query["viewer"] }>(query);
  const repositories = response.viewer.repositories.nodes;
  assert(repositories);

  const responseRepos = repositories.filter((r) => r).map((r) => convertRepoObject(r!));

  const output: QueryGithubReposResponseBody = {
    repos: responseRepos,
  };

  res.json(output);
}

function convertRepoObject(gqlRepo: Repository): ExternalGithubRepo {
  return {
    id: gqlRepo.id,
    name: gqlRepo.name,
    url: gqlRepo.url,
    description: gqlRepo.description,
    created_at: gqlRepo.createdAt,
    updated_at: gqlRepo.updatedAt,
    pushed_at: gqlRepo.pushedAt,
    owner: {
      id: gqlRepo.owner.id,
      login: gqlRepo.owner.login,
      avatar_url: gqlRepo.owner.avatarUrl,
    },
  };
}
