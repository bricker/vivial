import { Request, Response } from 'express';
import { Octokit } from 'octokit';
import { Blob, Query, Ref, Repository, Scalars } from '@octokit/graphql-schema';
import { GetGithubUrlContentRequestBody, GetGithubUrlContentResponseBody } from '@eave-fyi/eave-stdlib-ts/src/github-api/operations.js';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { EaveRequestState, getEaveState } from '@eave-fyi/eave-stdlib-ts/src/lib/request-state.js';
import headers from '@eave-fyi/eave-stdlib-ts/src/headers.js';
import { getInstallationId, createOctokitClient } from '../lib/octokit-util.js';
import { loadQuery } from '../lib/graphql-util.js';

export async function getSummary(req: Request, res: Response): Promise<void> {
  const eaveState = getEaveState(res);
  const eaveTeamId = req.header(headers.EAVE_TEAM_ID_HEADER)!; // presence already validated

  const input = <GetGithubUrlContentRequestBody>req.body;
  if (!input.url) {
    eaveLogger.error({ message: 'Invalid input', eaveState });
    res.sendStatus(400);
    return;
  }

  const installationId = await getInstallationId(eaveTeamId);
  if (installationId === null) {
    eaveLogger.error({ message: 'missing github installation id', eaveState });
    res.sendStatus(500);
    return;
  }
  const client = await createOctokitClient(installationId);
  const content = await getFileContent(client, input.url, eaveState);
  const output: GetGithubUrlContentResponseBody = { content };
  res.json(output);
}

/**
 * Fetch content of the file located at the URL `url`.
 * @returns null on GitHub API request failure
 */
async function getFileContent(client: Octokit, url: string, eaveState: EaveRequestState): Promise<string | null> {
  try {
    return getRawContent(client, url, eaveState);
  } catch (e: any) {
    eaveLogger.error({ message: e.stack, eaveState });
    return null;
  }
}

async function getRepositoryByUrl(client: Octokit, url: string, eaveState: EaveRequestState): Promise<Repository | null> {
  const query = await loadQuery('getResource');
  const variables: {
    resourceUrl: Scalars['URI'],
  } = {
    resourceUrl: url,
  };

  const response = await client.graphql<{ resource: Query['resource'] }>(query, variables);
  if (!response.resource) {
    eaveLogger.warn({ message: `Invalid url: ${url}`, eaveState });
    // Invalid URL
    return null;
  }

  // FIXME: This is not guaranteed to be a Repository
  const repository = <Repository>response.resource;
  if (!repository.owner?.login || !repository.name) {
    eaveLogger.warn({ message: `Resource not a repository: ${url}`, eaveState });
    // Invalid response
    return null;
  }

  return repository;
}

async function getFileInfoFromUrl(client: Octokit, repository: Repository, url: URL, eaveState: EaveRequestState): Promise<{ refName: string, treePath: string } | null> {
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
  const rest = url.pathname.split('/').slice(4);
  if (rest.length === 0) {
    eaveLogger.error({ message: `invalid url: ${url.toString()}`, eaveState });
    return null;
  }

  const refsQuery = await loadQuery('getRefs');

  for (let i = 0; i < rest.length; i += 1) {
    const numberOfSegments = i + 1;
    const candidateBranchName = rest.slice(0, numberOfSegments).join('/');

    const variables: {
      repoOwner: Scalars['String'],
      repoName: Scalars['String'],
      refPrefix: Scalars['String'],
      refQuery: Scalars['String']
    } = {
      repoOwner: repository.owner.login,
      repoName: repository.name,
      refPrefix: 'refs/heads/', // TODO: We need to check refs/tags/ too
      refQuery: candidateBranchName,
    };

    // eslint complains about await in for loop, but we're doing that deliberately because we need an iterator.
    // There's a probably a more javascript-y way to do it though
    /* eslint-disable-next-line */
    const response = await client.graphql<{ repository: Query['repository'] }>(refsQuery, variables);
    if (!response.repository || !response.repository.refs) {
      eaveLogger.warn({ message: `Invalid url: ${url}`, eaveState });
      // Invalid URL
      return null;
    }

    const refRepo = <Repository>response.repository;
    const refs = <Array<Ref>>refRepo.refs?.nodes;
    if (refs.length === 0) {
      eaveLogger.error({ message: 'no branches found', eaveState });
      return null;
    }

    if (refs.length === 1) {
      const branchName = refs[0]?.name;

      if (branchName === candidateBranchName) {
        // The filepath is everything after the branch name
        // `i` here is the index of the last path segment in the branch name
        const filePath = rest.slice(i + 1).join('/');
        // We're done, we found the branch
        return {
          refName: branchName,
          treePath: filePath,
        };
      }
    }
  }

  eaveLogger.warn({ message: `No branches matched ${url.toString()}`, eaveState });
  return null;
}

/**
 * Fetch github file content from `url` using the raw.githubusercontent.com feature
 * Returns null if `url` is not a path to a file (or if some other error was encountered).
 *
 * NOTE: raw.githubusercontent.com is ratelimitted by IP, not requesting user, so this wont scale far
 * https://github.com/github/docs/issues/8031#issuecomment-881427112
 */
async function getRawContent(client: Octokit, url: string, eaveState: EaveRequestState): Promise<string | null> {
  const urlComponents = new URL(url);

  // Replace /blob/ with /tree/ because the `resource` query doesn't recognize blob URLs.
  // This regex needs to be a bit more precise because it needs to catch /blob/ only in a specific location (the third path segment)
  urlComponents.pathname = urlComponents.pathname.replace(/^\/([^/]+)\/([^/]+)\/blob\//, '/$1/$2/tree/');
  const normalizedUrl = urlComponents.toString();

  const repository = await getRepositoryByUrl(client, normalizedUrl, eaveState);
  if (!repository) {
    eaveLogger.warn({ message: `Repository not found for ${url}`, eaveState });
    return null;
  }

  const fileInfo = await getFileInfoFromUrl(client, repository, urlComponents, eaveState);
  if (!fileInfo) {
    eaveLogger.warn({ message: `couldn't get file info for ${url}`, eaveState });
    return null;
  }

  const { refName, treePath } = fileInfo;

  const contentsQuery = await loadQuery('getFileContentsByPath');
  const variables: {
    repoOwner: Scalars['String'],
    repoName: Scalars['String'],
    expression: Scalars['String'],
  } = {
    repoOwner: repository.owner.login,
    repoName: repository.name,
    expression: `${refName}:${treePath}`,
  };

  const response = await client.graphql<{ repository: Query['repository'] }>(contentsQuery, variables);
  const objectRepository = <Repository>response.repository;
  if (!objectRepository) {
    eaveLogger.warn({ message: `Repository not found for ${url}`, eaveState });
    return null;
  }

  const gitObject = <Blob>objectRepository.object;
  if (!gitObject) {
    eaveLogger.warn({ message: `invalid git object for ${url}`, eaveState });
    return null;
  }

  const fileContent = gitObject.text;
  if (!fileContent) {
    eaveLogger.warn({ message: `invalid git object for ${url}`, eaveState });
    return null;
  }

  return fileContent;
}
