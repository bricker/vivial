import { GithubRepo } from "@eave-fyi/eave-stdlib-ts/src/core-api/models/github-repos.js";
import { GitHubOperationsContext } from "../../types.js";
import { Query, Repository, Scalars, TreeEntry } from "@octokit/graphql-schema";
import { loadQuery } from "../graphql-util.js";
import path from "path";

async function getExternalRepo({
  repo,
  ctx,
  octokit,
}: GitHubOperationsContext & { repo: GithubRepo }): Promise<Repository> {
  const query = await loadQuery("getRepo");
  const variables: {
    nodeId: Scalars["ID"]["input"];
  } = {
    nodeId: repo.external_repo_id,
  };

  const response = await octokit.graphql<{ node: Query["node"] }>(
    query,
    variables,
  );
  return <Repository>response.node;
}

async function getExpressAPIRootDirs({
  repo,
  octokit,
  ctx,
}: GithubApiCallerArgs): Promise<string[]> {
  const query = `"\\"express\\":" in:file filename:package.json repo:${repo.owner.login}/${repo.name}`;
  const response = await octokit.rest.search.code({
    q: query,
  });

  const dirs = response.data.items.map((i) => path.dirname(i.path));
  return dirs;
}

async function * recurseGitTree({
  treeRootDir,
  repo,
  octokit,
  ctx,
}: GitHubOperationsContext & { treeRootDir: string; repo: Repository }): AsyncGenerator<TreeEntry> {
  const query = await loadQuery("getGitObject");
  const variables: {
    repoOwner: Scalars["String"]["input"];
    repoName: Scalars["String"]["input"];
    expression: Scalars["String"]["input"];
  } = {
    repoOwner: repo.owner.login,
    repoName: repo.name,
    expression: `${repo.defaultBranchRef!.name}:${treeRootDir}`,
  };

  const response = await octokit.graphql<{ repository: Query["repository"] }>(
    query,
    variables,
  );
  const repository = <Repository>response.repository;
  assertIsTree(repository.object);

  const tree = repository.object;
  const blobEntries = tree.entries?.filter((e) => isBlob(e.object));
  const subTrees = tree.entries?.filter((e) => isTree(e.object));

  // BFS
  if (blobEntries) {
    for (const blobEntry of blobEntries) {
      // TODO: How to design this function to return a TreeEntry narrowed to `TreeEntry.object.__typename === "Blob"`, so the caller doesn't have to assert?
      yield blobEntry;
    }
  }

  if (subTrees) {
    for (const subTree of subTrees) {
      yield* recurseGitTree({ treeRootDir: subTree.path!, repo, octokit, ctx });
    }
  }
}



async function getExpressAPIRootFile({
  apiRootDir,
  repo,
  parser,
  octokit,
  ctx,
}: GithubApiCallerArgs & { apiRootDir: string }): Promise<CodeFile | null> {
  for await (const treeEntry of recurseGitTree({ treeRootDir: apiRootDir, repo, octokit, ctx })) {
    const blob = treeEntry.object;
    assertIsBlob(blob);
    if (!blob.text) {
      // text is either null (binary object), undefined (not in response), or empty string (empty file). Either way, move on.
      continue
    }

    assert(treeEntry.path, "unexpected missing path property");
    const file = new CodeFile({ path: treeEntry.path, contents: blob.text });
    const isExpressRoot = parser.testExpressRootFile({ file });
    if (isExpressRoot) {
      // We found the file; Early-exit the whole function
      return new CodeFile({ path: treeEntry.path, contents: blob.text });
    }
  }

  return null;
}
