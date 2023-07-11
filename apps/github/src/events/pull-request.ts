import { PullRequestEvent } from '@octokit/webhooks-types';
import { GitHubOperationsContext } from '../types.js';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import OpenAIClient, { OpenAIModel } from '@eave-fyi/eave-stdlib-ts/src/openai.js';
import { Query, Scalars, Blob, Repository, PullRequest, PullRequestChangedFileConnection, PullRequestChangedFile, PatchStatus } from '@octokit/graphql-schema';
import * as GraphQLUtil from '../lib/graphql-util.js';

import { appConfig } from '../config.js';
import { getGithubInstallation } from '@eave-fyi/eave-stdlib-ts/src/core-api/operations/github.js';


/**
 * Receives github webhook pull_request events.
 * https://docs.github.com/en/webhooks-and-events/webhooks/webhook-events-and-payloads?actionType=closed#pull_request
 * 
 * Features:
 * Checks if closed PR was merged. If so, update inline file docs
 * for each file with code changes. 
 */
export default async function handler(event: PullRequestEvent, context: GitHubOperationsContext) {
  // verify PR was closed and merged
  if (event.action !== 'closed' || !event.pull_request.merged) {
    return;
  }
  
  const repoOwner = event.repository.owner.name;
  const repoName = event.repository.name;

  const { ctx, octokit } = context;
  eaveLogger.debug('Processing push', ctx);

  // find files changed in PR commits
  let keepPaginating = true;
  let filePaths: Array<string> = [];
  const filesQuery = await GraphQLUtil.loadQuery('listFilesInPullRequest');
  const filesQueryVariables: {
    repoOwner: Scalars['String'],
    repoName: Scalars['String'],
    prNumber: Scalars['Int'], 
    batchSize: Scalars['Int'],
    after?: Scalars['String'],
  } = {
    repoOwner,
    repoName,
    prNumber: event.pull_request.number,
    batchSize: 50, // max 100
  };

  // paginate to collect all files
  while (keepPaginating) {
    const queryResp = await octokit.graphql<{ repository: Query['repository'] }>(filesQuery, filesQueryVariables);
    const prRepo = <Repository>queryResp.repository;
    const pr = <PullRequest>prRepo?.pullRequest;
    const prFilesConnection = <PullRequestChangedFileConnection>pr?.files;
    const prFileNodes = <Array<PullRequestChangedFile>>prFilesConnection?.nodes;

    if (!prFileNodes) {
      eaveLogger.error('Failed to acquire file list from PR while processing PR merge event');
      return;
    }

    // extract files that new docs updates
    const documentableFiles = prFileNodes.filter((f) => f.changeType === 'ADDED' || f.changeType === 'MODIFIED');

    // TODO: extract files that we want inline comments in


    filePaths = filePaths.concat(documentableFiles.map((f) => f.path));

    // continue while files fill page size
    keepPaginating = prFilesConnection.pageInfo.hasNextPage;
    // assign query vars `after` field so that next query will continue paginating
    // files where the previous request left off
    filesQueryVariables.after = prFilesConnection.pageInfo.endCursor;
  }


  // update docs in each file
  const openaiClient = await OpenAIClient.getAuthedClient();
  const contentsQuery = await GraphQLUtil.loadQuery('getFileContentsByPath');

  await Promise.all(filePaths.map(async (fpath) => {
    const contentsQueryVariables: {
      repoOwner: Scalars['String'],
      repoName: Scalars['String'],
      expression: Scalars['String'],
    } = {
      repoOwner: event.repository.owner.name,
      repoName: event.repository.name,
      expression: `${event.pull_request.base.ref}:${fpath}`, // branch:fpath
    };

    const response = await octokit.graphql<{ repository: Query['repository'] }>(contentsQuery, contentsQueryVariables);
    const objectRepository = <Repository>response.repository;
    const gitObject = <Blob>objectRepository?.object;
    const fileContent = gitObject?.text;
    if (!fileContent) {
      eaveLogger.error(`Error fetching file content for ${fpath}`, ctx); // TODO: is it ok to log file name/path? is that too sensitive?
      return;
    }
    
    // see if existing docs

    // write new docs

  }));


  // branch off event.pull_request.base.ref 
  // https://stackoverflow.com/a/9513594/9718199

  // commit changes
  // https://stackoverflow.com/a/46760154/9718199
  // https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28#create-or-update-file-contents

  // open PR against event.pull_request.base.ref
  // https://docs.github.com/en/rest/pulls/pulls?apiVersion=2022-11-28#create-a-pull-request


}