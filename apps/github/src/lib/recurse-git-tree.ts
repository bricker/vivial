import { Blob, Commit, GitObject, Query, Repository, Scalars, Tag, Tree } from "@octokit/graphql-schema";
import { loadQuery } from "../lib/graphql-util.js";
import { GitHubOperationsContext } from "../types.js";

export async function recurseGitTree({ octokit, repo, ctx }: GitHubOperationsContext & { repo: Repository }) {
  const query = await loadQuery("getTree");
  const variables: {
    repoOwner: Scalars["String"]["input"];
    repoName: Scalars["String"]["input"];
    expression: Scalars["String"]["input"];
  } = {
    repoOwner: repo.owner.login,
    repoName: repo.name,
    expression: "main:path/path/tree",
  };

  const response = await octokit.graphql<{ repository: Query["repository"] }>(query, variables);
  const repository = <Repository>response.repository;

  if (!repository.object) {
    throw new Error("Unexpected empty object field");
  }

  if (isTree(repository.object)) {
    const tree = repository.object;
    await recurseGitTree({ tree, repo, octokit, ctx });
  } else if (isBlob(repository.object)) {

  }

  // FIXME:
}

function isTree(obj: { __typename?: string }): obj is Tree {
  return obj.__typename === "Tree";
}

function isBlob(obj: { __typename?: string }): obj is Blob {
  return obj.__typename === "Blob";
}
