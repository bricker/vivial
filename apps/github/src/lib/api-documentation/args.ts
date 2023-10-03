import { GithubRepo } from "@eave-fyi/eave-stdlib-ts/src/core-api/models/github-repos.js";
import { Repository } from "@octokit/graphql-schema";

export type EaveGithubRepoArg = { eaveGithubRepo: GithubRepo };
export type ExternalGithubRepoArg = { externalGithubRepo: Repository };
