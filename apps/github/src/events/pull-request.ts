import { PullRequestEvent } from '@octokit/webhooks-types';
import { GitHubOperationsContext } from '../types.js';
import Promise from 'bluebird';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import OpenAIClient, { OpenAIModel, dedent } from '@eave-fyi/eave-stdlib-ts/src/openai.js';
import { Query, Scalars, Blob, Repository, PullRequest, PullRequestChangedFileConnection, PullRequestChangedFile, PatchStatus, Mutation, FileChanges, CommitMessage, CommittableBranch } from '@octokit/graphql-schema';
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
  // proceed only if event was PR being closed and merged
  if (event.action !== 'closed' || !event.pull_request.merged) {
    return;
  }

  const repoOwner = event.repository.owner.name!;
  const repoName = event.repository.name;

  const { ctx, octokit } = context;
  const openaiClient = await OpenAIClient.getAuthedClient();
  eaveLogger.debug('Processing github pull_request event', ctx);

  let keepPaginating = true;
  let filePaths: Array<string> = [];
  const filesQuery = await GraphQLUtil.loadQuery('getFilesInPullRequest');
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

  // paginate to collect all files from the PR
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

    const documentableFiles = await Promise.filter(prFileNodes, async (f) => {
      // dont document files that aren't new or modified
      if (!(f.changeType === 'ADDED' || f.changeType === 'MODIFIED')) {
        return false;
      }

      // TODO: would we get ratelimited if we tried to do all gpt prompts in parallel after all file paths obtained?
      // TODO: test prompt allowing test files to be documented
      const prompt = dedent(
        `Given a file path, determine whether that file typically needs function-level code comments.
        Respond with only YES, or NO. Config, generated and test files do not need documentation.

        src/main.c: YES
        README.md: NO
        scripts/setup.sh: NO
        bin/run: NO
        frontend/tests/LogicTests.js: NO
        ${f.path}:`,
      );
      const openaiResponse = await openaiClient.createChatCompletion({
        parameters: {
          messages: [
            { role: 'user', content: prompt },
          ],
          model: OpenAIModel.GPT4,
        },
        ctx,
      });

      return openaiResponse === 'YES';
    });

    filePaths = filePaths.concat(documentableFiles.map((f) => f.path));

    // assign query vars `after` field so that next query will continue paginating
    // files where the previous request left off
    filesQueryVariables.after = prFilesConnection.pageInfo.endCursor || undefined; // convert null to undefined for happy types
    keepPaginating = prFilesConnection.pageInfo.hasNextPage;
  }

  // update docs in each file
  const contentsQuery = await GraphQLUtil.loadQuery('getFileContentsByPath');
  await Promise.all(filePaths.map(async (fpath) => {
    const contentsQueryVariables: {
      repoOwner: Scalars['String'],
      repoName: Scalars['String'],
      expression: Scalars['String'],
    } = {
      repoOwner,
      repoName,
      expression: `${event.pull_request.base.ref}:${fpath}`,
    };

    const response = await octokit.graphql<{ repository: Query['repository'] }>(contentsQuery, contentsQueryVariables);
    const objectRepository = <Repository>response.repository;
    const gitObject = <Blob>objectRepository?.object;
    const fileContent = gitObject?.text;
    if (!fileContent) {
      // TODO: this error probs expected for images etc, but those should be filtered out by earlier step? 
      //       or maybe files that shouldnt get commetns will have to be filtered out in this step?
      eaveLogger.error(`Error fetching file content for ${fpath}`, ctx); // TODO: is it ok to log file name/path? is that too sensitive?
      return; // exits just this iteration of map
    }

    // see if existing docs

    // write new docs

    // encode as b64 bcus thats how github likes it
  }));

  // branch off branch that PR was merged into (event.pull_request.base)
  // https://docs.github.com/en/graphql/reference/mutations#createref
  const createBranchMutation = await GraphQLUtil.loadQuery('createBranch');
  const commitHeadId = event.pull_request.base.sha; // TODO: can this be used as commit oid?
  const createBranchParameters: {
    repoId: Scalars['ID'],
    branchName: Scalars['String'],
    commitHeadId: Scalars['GitObjectID'],
  } = {
    commitHeadId,
    branchName: `refs/heads/eave/function-docs/${event.pull_request.number}`,
    repoId: event.repository.id.toString(),
  };
  const branchResp = await octokit.graphql<{ branch: Mutation['createRef'] }>(createBranchMutation, createBranchParameters);
  const docsBranch = branchResp.branch?.ref;
  if (!docsBranch) {
    eaveLogger.error(`Failed to create branch in ${repoOwner}/${repoName}`);
    return;
  }

  // commit changes
  // https://docs.github.com/en/graphql/reference/mutations#createcommitonbranch
  const createCommitMutation = await GraphQLUtil.loadQuery('createCommitOnBranch');
  const createCommitParameters: {
    branch: CommittableBranch,
    headOid: Scalars['GitObjectID'],
    message: CommitMessage,
    fileChanges: FileChanges,
  } = {
    branch: { branchName: docsBranch.name, repositoryNameWithOwner: `${repoOwner}/${repoName}` },
    headOid: docsBranch.target!.oid,
    message: { headline: 'docs: automated update [ci skip]' },
    fileChanges: {
      additions: [ // TODO: map/zip
        {
          path: fpath,
          contents: b64Content,
        },
      ],
    },
  };
  const commitResp = await octokit.graphql<{ commit: Mutation['createCommitOnBranch'] }>(createCommitMutation, createCommitParameters);
  if (!commitResp.commit?.commit?.oid) {
    eaveLogger.error(`Failed to create commit in ${repoOwner}/${repoName}`);
    // TODO: cleanup branch?
    return;
  }

  // open PR against event.pull_request.base.ref
  // TODO: veirfy all optional params i didnt include in gql have sensible/expected default values
  // https://docs.github.com/en/graphql/reference/mutations#createpullrequest
  const createPrMutation = await GraphQLUtil.loadQuery('createPullRequest');
  const createPrParameters: {
    baseRefName: Scalars['String'],
    body: Scalars['String'],
    headRefName: Scalars['String'],
    repoId: Scalars['ID'],
    title: Scalars['String'],
  } = {
    repoId: event.repository.id.toString(),
    baseRefName: event.pull_request.base.ref, // TODO: verify value of base.ref is the ref name, not something else.. (probs does require refs/heads/ prefix)
    headRefName: docsBranch.name,
    title: 'docs: Eave auto code documentation update', // TODO: worksoho
    body: `Your new Eave docs based on changes from PR #${event.pull_request.number}`, // TODO: workshop
  };
  const prResp = await octokit.graphql<{ pr: Mutation['createPullRequest'] }>(createPrMutation, createPrParameters);
  if (!prResp.pr?.pullRequest?.number) {
    eaveLogger.error(`Failed to create PR in ${repoOwner}/${repoName}`);
    // TODO: cleanup branch?
    return;
  }
}
