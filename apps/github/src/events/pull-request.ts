import { PullRequestEvent } from '@octokit/webhooks-types';
import fs from 'fs';
import path from 'path';
import eaveLogger, { LogContext } from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import OpenAIClient, { OpenAIModel, dedent } from '@eave-fyi/eave-stdlib-ts/src/transformer-ai/openai.js';
import {
  Query,
  Scalars,
  Blob,
  Repository,
  PullRequest,
  PullRequestChangedFileConnection,
  PullRequestChangedFile,
  Mutation,
  FileChanges,
  CommitMessage,
  CommittableBranch,
} from '@octokit/graphql-schema';
import { Octokit } from 'octokit';
import * as AIUtil from '@eave-fyi/eave-stdlib-ts/src/transformer-ai/util.js';
import { logEvent } from '@eave-fyi/eave-stdlib-ts/src/analytics.js';
import { writeDocsIntoFileString, parseFunctionsAndComments } from '../parsing/function-parsing.js';
import { GitHubOperationsContext } from '../types.js';
import * as GraphQLUtil from '../lib/graphql-util.js';
import { appConfig } from '../config.js';

const eavePrTitle = 'docs: Eave inline code documentation update';

/**
 * Receives github webhook pull_request events.
 * https://docs.github.com/en/webhooks-and-events/webhooks/webhook-events-and-payloads?actionType=closed#pull_request
 *
 * Features:
 * Checks if closed PR was merged. If so, update inline file docs
 * for each file with code changes.
 */
export default async function handler(event: PullRequestEvent, context: GitHubOperationsContext) {
  if (event.action !== 'closed') {
    return;
  }
  const { ctx, octokit } = context;

  // don't open more docs PRs from other Eave PRs getting merged
  // TODO: perform this check using event.sender.id instead for broader metric capture. compare to app id?? (app_id diff for prod vs stage)
  if (event.pull_request.title === eavePrTitle) {
    const interaction = event.pull_request.merged ? 'merged' : 'closed';
    await logEvent({
      event_name: 'github_eave_pr_interaction',
      event_time: new Date().toISOString(),
      event_description: `A GitHub PR opened by Eave was ${interaction}`,
      event_source: 'github webhook pull_request event',
      opaque_params: JSON.stringify({ interaction }),
      eave_account_id: ctx?.eave_account_id,
      eave_team_id: ctx?.eave_team_id,
      eave_env: appConfig.eaveEnv,
      opaque_eave_ctx: JSON.stringify(ctx),
    }, ctx);
    return;
  }

  // proceed only if PR commits were merged
  if (!event.pull_request.merged) {
    return;
  }

  const repoOwner = event.repository.owner.login;
  const repoName = event.repository.name;
  const repoId = event.repository.node_id.toString();

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
      eaveLogger.error('Failed to acquire file list from PR while processing PR merge event', ctx);
      return;
    }

    const documentableFiles: Array<PullRequestChangedFile> = [];
    for (const f of prFileNodes) {
      // dont document files that aren't new or modified
      if (!(f.changeType === 'ADDED' || f.changeType === 'MODIFIED')) {
        continue;
      }

      // TODO: would we get ratelimited if we tried to do all gpt prompts in parallel after all file paths obtained?
      // TODO: test feature behavior allowing test files to be documented. Should we allow that?
      const prompt = dedent(
        `Given a file path, determine whether that file typically needs function-level code comments.
        Respond with only YES, or NO. Config, generated, and test files do not need documentation.

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
          max_tokens: 10,
        },
        ctx,
      });

      if (openaiResponse === 'YES') {
        documentableFiles.push(f);
      }
    }

    filePaths = filePaths.concat(documentableFiles.map((f) => f.path));

    // assign query vars `after` field so that next query will continue paginating
    // files where the previous request left off
    filesQueryVariables.after = prFilesConnection.pageInfo.endCursor || undefined; // convert null to undefined for happy types
    keepPaginating = prFilesConnection.pageInfo.hasNextPage;
  }

  // update docs in each file
  const contentsQuery = await GraphQLUtil.loadQuery('getFileContentsByPath');
  const b64UpdatedContent = await Promise.all(filePaths.map(async (fpath): Promise<string | null> => {
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
      eaveLogger.error(`Error fetching file content in ${repoOwner}/${repoName}`, ctx);
      return null; // exits just this iteration of map
    }

    const updatedFileContent = await updateDocumentation(fileContent, fpath, openaiClient, ctx);
    if (!updateDocumentation) {
      return null;
    }

    // encode new content as b64 bcus thats how github likes it
    return Buffer.from(updatedFileContent!).toString('base64');
  }));

  // branch off the PR merge commit (should be base branch HEAD commit since PR just merged)
  // https://docs.github.com/en/graphql/reference/mutations#createref
  const createBranchMutation = await GraphQLUtil.loadQuery('createBranch');
  const createBranchParameters: {
    repoId: Scalars['ID'],
    branchName: Scalars['String'],
    commitHeadId: Scalars['GitObjectID'],
  } = {
    commitHeadId: event.pull_request.merge_commit_sha,
    branchName: `refs/heads/eave/auto-docs/${event.pull_request.number}`,
    repoId,
  };
  const branchResp = await octokit.graphql<{ createRef: Mutation['createRef'] }>(createBranchMutation, createBranchParameters);
  const docsBranch = branchResp.createRef?.ref;
  if (!docsBranch) {
    eaveLogger.error(`Failed to create branch in ${repoOwner}/${repoName}`, ctx);
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
    message: { headline: 'docs: automated update [ci skip]' }, // TODO: should skip?
    fileChanges: {
      additions: filePaths.map((fpath, i) => {
        return {
          path: fpath,
          contents: b64UpdatedContent[i],
        };
      }).filter((adds) => {
        // remove entries w/ null content from content fetch failures
        return adds.contents !== null;
      }),
    },
  };
  const commitResp = await octokit.graphql<{ createCommitOnBranch: Mutation['createCommitOnBranch'] }>(createCommitMutation, createCommitParameters);
  if (!commitResp.createCommitOnBranch?.commit?.oid) {
    eaveLogger.error(`Failed to create commit in ${repoOwner}/${repoName}`, ctx);
    await deleteBranch(octokit, docsBranch!.id);
    return;
  }

  // open new PR against event.pull_request.base.ref (same base as PR that triggered this event)
  // https://docs.github.com/en/graphql/reference/mutations#createpullrequest
  const createPrMutation = await GraphQLUtil.loadQuery('createPullRequest');
  const createPrParameters: {
    baseRefName: Scalars['String'],
    body: Scalars['String'],
    headRefName: Scalars['String'],
    repoId: Scalars['ID'],
    title: Scalars['String'],
  } = {
    repoId,
    baseRefName: event.pull_request.base.ref,
    headRefName: docsBranch!.name,
    title: eavePrTitle,
    body: `Your new code docs based on changes from PR #${event.pull_request.number}`,
  };
  const prResp = await octokit.graphql<{ createPullRequest: Mutation['createPullRequest'] }>(createPrMutation, createPrParameters);
  if (!prResp.createPullRequest?.pullRequest?.number) {
    eaveLogger.error(`Failed to create PR in ${repoOwner}/${repoName}`, ctx);
    await deleteBranch(octokit, docsBranch!.id);
    return;
  }
}

// https://docs.github.com/en/graphql/reference/mutations#deleteref
async function deleteBranch(octokit: Octokit, branchNodeId: string) {
  const query = await GraphQLUtil.loadQuery('deleteBranch');
  const params: {
    refNodeId: Scalars['ID'],
  } = {
    refNodeId: branchNodeId,
  };
  await octokit.graphql<{ resp: Mutation['deleteRef'] }>(query, params);
}

/**
 * Given the current content of a file, returns the same file
 * content but with the documentation updated to reflect any code changes.
 *
 * @param currContent a file's content in plaintext
 * @param filePath file path correlated with `currContent` file content
 * @param openaiClient
 * @param ctx extra context for more detailed logs
 * @returns the same code content as `currContent` but with doc strings updated, or null if unable to create updated document
 */
async function updateDocumentation(currContent: string, filePath: string, openaiClient: OpenAIClient, ctx: LogContext): Promise<string | null> {
  // load language from file extension map file
  // TODO: add to warmup
  const extensionMapString = await fs.promises.readFile('./languages.json', { encoding: 'utf8' });
  const extensionMap = JSON.parse(extensionMapString);
  const extName = `${path.extname(filePath).toLowerCase()}`;
  const flang: string = extensionMap[extName];
  if (!flang) {
    // file extension not found in the map file, which makes it impossible for us to
    // put docs in a syntactially valid comment; exit early
    eaveLogger.error(`No matching language found for file extension: "${extName}"`);
    return null;
  }

  const parsedData = parseFunctionsAndComments(currContent, extName, flang);
  if (parsedData.length === 0) {
    eaveLogger.error(`Unable to parse ${flang} from ${extName} file`);
    return null;
  }

  // update parsedData objects in place w/ updatedCommentStrings
  await Promise.all(parsedData.map(async (funcData) => {
    // convert long function strings to a summary for docs writing to prevent AI from getting overwhelmed by
    // implementation details in raw code file (and to account for functions longer than model context)
    const summarizedFunction = await AIUtil.rollingSummary(openaiClient, funcData.func);

    // update docs, or write new ones if currDocs is empty/undefined
    // TODO: refine prompt
    // TODO: account for summarized function
    // TODO: add/generate typical doc comment params etc boilerplate?
    // TODO: experiment performance qulaity on dif types of comments:
    //      (1. update own comment 2. write from scratch 3. update existing detailed docs 4. fix slightly incorrect docs)
    const docsPrompt = dedent(
      `Write a 2-3 sentence overview of the purpose of this function.

      ===
      ${summarizedFunction}
      ===`,
    );
    const newDocsResponse = await openaiClient.createChatCompletion({
      parameters: {
        messages: [
          {
            role: 'user',
            content: docsPrompt,
          },
        ],
        model: OpenAIModel.GPT4,
        temperature: 0.2,
      },
      ctx,
    });

    // if there were already existing docs, update them using newly written docs
    let updatedDocs = newDocsResponse;
    if (funcData.comment) {
      updatedDocs = await openaiClient.createChatCompletion({
        parameters: {
          messages: [
            {
              role: 'user',
              content: dedent(
                `Merge these two chunks of documentation together into a paragraph, maintaining the important information. 
                If there are any conflicts of content, prefer the new documentation.
                
                Old documentation:
                ===
                ${funcData.comment}
                ===
                
                New documentation:
                ===
                ${newDocsResponse}
                ===`,
              ),
            },
          ],
          model: OpenAIModel.GPT4,
          temperature: 0.2,
        },
        ctx,
      });
    }

    const updatedDocsComment = await openaiClient.createChatCompletion({
      parameters: {
        messages: [
          {
            role: 'user',
            content: dedent(
              `Convert the following text to a multi-line doc comment valid in the programming language ${flang}. Respond with only the doc comment.
              
              ${updatedDocs}`,
            ),
          },
        ],
        model: OpenAIModel.GPT4,
        temperature: 0.2,
      },
      ctx,
    });

    funcData.updatedComment = updatedDocsComment;
  }));

  // write `updatedComment` data back into currContent string
  return writeDocsIntoFileString(currContent, parsedData);
}
