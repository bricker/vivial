import { GetGithubUrlContentRequestBody, GetGithubUrlContentResponseBody } from "@eave-fyi/eave-stdlib-ts/src/github-api/operations/get-content.js";
import { LogContext, eaveLogger } from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import { Blob, Query, Ref, Repository, Scalars } from "@octokit/graphql-schema";
import { Request, Response } from "express";
import { Octokit } from "octokit";
import { loadQuery } from "../lib/graphql-util.js";
import { createTeamOctokitClient } from "../lib/octokit-util.js";

export async function getContentSummaryHandler(req: Request, res: Response): Promise<void> {
  const ctx = LogContext.load(res);
  const octokit = await createTeamOctokitClient(req, ctx);

  const input = <GetGithubUrlContentRequestBody>req.body;
  if (!input.url) {
    eaveLogger.error("Invalid input", ctx);
    res.sendStatus(400);
    return;
  }

  const content = await getFileContent(octokit, input.url, ctx);
  const output: GetGithubUrlContentResponseBody = { content };
  res.json(output);
}

/**
 * Fetch content of the file located at the URL `url`.
 * @returns null on GitHub API request failure
 */
async function getFileContent(client: Octokit, url: string, ctx: LogContext): Promise<string | null> {
  try {
    return getRawContent(client, url, ctx);
  } catch (e: any) {
    eaveLogger.error(e, ctx);
    return null;
  }
}

async function getRepositoryByUrl(client: Octokit, url: string, ctx: LogContext): Promise<Repository | null> {
  const query = await loadQuery("getResource");
  const variables: {
    resourceUrl: Scalars["URI"]["input"];
  } = {
    resourceUrl: url,
  };

  const response = await client.graphql<{ resource: Query["resource"] }>(query, variables);
  if (!response.resource) {
    eaveLogger.warning(`Invalid url: ${url}`, ctx);
    // Invalid URL
    return null;
  }

  // FIXME: This is not guaranteed to be a Repository
  const repository = <Repository>response.resource;
  if (!repository.owner?.login || !repository.name) {
    eaveLogger.warning(`Resource not a repository: ${url}`, ctx);
    // Invalid response
    return null;
  }

  return repository;
}

async function getFileInfoFromUrl(client: Octokit, repository: Repository, url: URL, ctx: LogContext): Promise<{ refName: string; treePath: string } | null> {
  // Given a path: /owner/repo/tree/...
  // The path segments 4+ (index 3+) are what we're interested in.
  // We'll start with just the first path segment. In many cases, this will be the branch name.
  // However, it's common for developers to prefix branch names with their name, eg `bcr/some-branch-name`
  // To handle this case, we're going to get all of the branch names matching that first patch segment.
  // if there are more than one, then we'll grab the next path segment, then we'll get all the branch names matching
  // the first two path segments. We'll continue to do this until we receive just one result.
  // This leans on the fact that a branch can't have the same name as a git ref directory. For example:
  //
  // In this branch name: bcr/2305/my-branch
  // - `bcr` is a directory. We therefore cannot have a branch called `bcr`
  // - `bcr/2305` is also a directory, so there is guaranteed not to be a branch called `bcr/2305`
  // - `bcr/2305/my-branch` is the full branch name.
  //
  // These are actually stored as directories on the filesystem:
  //
  // $ ls .git/refs/heads/bcr/
  // 2303  2304  2305
  //
  // $ ls .git/refs/heads/bcr/2304:
  // access-tokens    delete-subscription  more-auth       setupscript-updates  slack-updates
  // atlassian-oauth  eaveauth             script-updates  slack-auth

  // Slice from 4 because path starts with a slash and gives an empty string as the first element, eg:
  // '/owner/repo/tree/some/branch' -> ['', 'owner', 'repo', tree', 'some', 'branch']
  const rest = url.pathname.split("/").slice(4);
  if (rest.length === 0) {
    eaveLogger.error(`invalid url: ${url.toString()}`, ctx);
    return null;
  }

  const refsQuery = await loadQuery("getRefs");

  for (let i = 0; i < rest.length; i += 1) {
    const numberOfSegments = i + 1;
    const candidateBranchName = rest.slice(0, numberOfSegments).join("/");

    const variables: {
      repoOwner: Scalars["String"]["input"];
      repoName: Scalars["String"]["input"];
      refPrefix: Scalars["String"]["input"];
      refQuery: Scalars["String"]["input"];
    } = {
      repoOwner: repository.owner.login,
      repoName: repository.name,
      refPrefix: "refs/heads/", // TODO: We need to check refs/tags/ too
      refQuery: candidateBranchName,
    };

    // eslint complains about await in for loop, but we're doing that deliberately because we need an iterator.
    // There's a probably a more javascript-y way to do it though
    /* eslint-disable-next-line */
    const response = await client.graphql<{ repository: Query["repository"] }>(refsQuery, variables);
    if (!response.repository || !response.repository.refs) {
      eaveLogger.warning(`Invalid url: ${url}`, ctx);
      // Invalid URL
      return null;
    }

    const refRepo = <Repository>response.repository;
    const refs = <Array<Ref>>refRepo.refs?.nodes;
    if (refs.length === 0) {
      eaveLogger.error("no branches found", ctx);
      return null;
    }

    if (refs.length === 1) {
      const branchName = refs[0]?.name;

      if (branchName === candidateBranchName) {
        // The filepath is everything after the branch name
        // `i` here is the index of the last path segment in the branch name
        const filePath = rest.slice(i + 1).join("/");
        // We're done, we found the branch
        return {
          refName: branchName,
          treePath: filePath,
        };
      }
    }
  }

  eaveLogger.warning(`No branches matched ${url.toString()}`, ctx);
  return null;
}

/**
 * Fetch github file content from a github `url` to a file.
 * Returns null if `url` is not a path to a file (or if some other error was encountered).
 */
async function getRawContent(client: Octokit, url: string, ctx: LogContext): Promise<string | null> {
  const urlComponents = new URL(url);

  // Replace /blob/ with /tree/ because the `resource` query doesn't recognize blob URLs.
  // This regex needs to be a bit more precise because it needs to catch /blob/ only in a specific location (the third path segment)
  urlComponents.pathname = urlComponents.pathname.replace(/^\/([^/]+)\/([^/]+)\/blob\//, "/$1/$2/tree/");
  const normalizedUrl = urlComponents.toString();

  const repository = await getRepositoryByUrl(client, normalizedUrl, ctx);
  if (!repository) {
    eaveLogger.warning(`Repository not found for ${url}`, ctx);
    return null;
  }

  const fileInfo = await getFileInfoFromUrl(client, repository, urlComponents, ctx);
  if (!fileInfo) {
    eaveLogger.warning(`couldn't get file info for ${url}`, ctx);
    return null;
  }

  const { refName, treePath } = fileInfo;

  const contentsQuery = await loadQuery("getFileContentsByPath");
  const variables: {
    repoOwner: Scalars["String"]["input"];
    repoName: Scalars["String"]["input"];
    expression: Scalars["String"]["input"];
  } = {
    repoOwner: repository.owner.login,
    repoName: repository.name,
    expression: `${refName}:${treePath}`,
  };

  const response = await client.graphql<{ repository: Query["repository"] }>(contentsQuery, variables);
  const objectRepository = <Repository>response.repository;
  if (!objectRepository) {
    eaveLogger.warning(`Repository not found for ${url}`, ctx);
    return null;
  }

  const gitObject = <Blob>objectRepository.object;
  if (!gitObject) {
    eaveLogger.warning(`invalid git object for ${url}`, ctx);
    return null;
  }

  const fileContent = gitObject.text;
  if (!fileContent) {
    eaveLogger.warning(`invalid git object for ${url}`, ctx);
    return null;
  }

  return fileContent;
}
