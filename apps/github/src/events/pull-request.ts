import { PullRequestEvent } from '@octokit/webhooks-types';
import bluebird from 'bluebird';
import fs from 'fs';
import path from 'path';
import eaveLogger, { LogContext } from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import OpenAIClient, { OpenAIModel, dedent } from '@eave-fyi/eave-stdlib-ts/src/openai.js';
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
import { GitHubOperationsContext } from '../types.js';
import * as GraphQLUtil from '../lib/graphql-util.js';

const eavePrTitle = 'docs: Eave auto code documentation update'; // TODO: workshop

/**
 * Receives github webhook pull_request events.
 * https://docs.github.com/en/webhooks-and-events/webhooks/webhook-events-and-payloads?actionType=closed#pull_request
 *
 * Features:
 * Checks if closed PR was merged. If so, update inline file docs
 * for each file with code changes.
 */
export default async function handler(event: PullRequestEvent, context: GitHubOperationsContext) {
  // TODO: gather analytics on how many eave PRs are merged vs closed w/o merge?
  // don't open more docs PRs from other Eave PRs
  if (event.pull_request.title === eavePrTitle) {
    return;
  }

  // proceed only if event was PR being closed and merged
  if (event.action !== 'closed' || !event.pull_request.merged) {
    return;
  }

  const repoOwner = event.repository.owner.login;
  const repoName = event.repository.name;
  const repoId = event.repository.node_id.toString();

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
      eaveLogger.error('Failed to acquire file list from PR while processing PR merge event', ctx);
      return;
    }

    const documentableFiles = await bluebird.filter(prFileNodes, async (f) => {
      // dont document files that aren't new or modified
      if (!(f.changeType === 'ADDED' || f.changeType === 'MODIFIED')) {
        return false;
      }

      // TODO: would we get ratelimited if we tried to do all gpt prompts in parallel after all file paths obtained?
      // TODO: test feature behavior allowing test files to be documented
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
          max_tokens: 10,
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
  let b64UpdatedContent = await bluebird.all(filePaths.map(async (fpath): Promise<string | null> => {
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
      eaveLogger.error(`Error fetching file content in ${repoOwner}/${repoName}`, ctx); // TODO: is it ok to log this? is that too sensitive? is it even helpful to us?
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
    body: `Your new code docs based on changes from PR #${event.pull_request.number}`, // TODO: workshop
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
 * @returns the same code content as `currContent` but with doc strings updated. null if unable to create updated document
 */
async function updateDocumentation(currContent: string, filePath: string, openaiClient: OpenAIClient, ctx: LogContext): Promise<string | null> {
  // load language from file extension map file
  const extensionMapString = await fs.promises.readFile('./languages.json', { encoding: 'utf8' }); // TODO: is there a better way to do this?
  const extensionMap = JSON.parse(extensionMapString);
  const flang: string = extensionMap[`${path.extname(filePath)}`];
  if (!flang) {
    // file extension not found in the map file, which makes it impossible for us to
    // put docs in a syntactially valid comment; exit early
    return null;
  }

  /*
    Extract existing docs; if there are any.
    Assumes that top-of-file docs will begin on line 1 of the file,
    and will continue until the first empty line, at which point
    we can separate the top-of-file docs from the rest of the code file.
  */
  const fileLines = currContent.split('\n');
  const commentPrompt = dedent(
    `Is the first line of this code file a comment in the programming language ${flang}? Respond only with YES or NO.

    \`\`\`
    ${fileLines[0]}
    \`\`\``,
  );
  const commentResponse = await openaiClient.createChatCompletion({
    parameters: {
      messages: [
        { role: 'user', content: commentPrompt },
      ],
      model: OpenAIModel.GPT4,
      max_tokens: 10,
      temperature: 0.1,
    },
  });

  let currDocs = '';
  let isolatedContent: string;
  if (commentResponse === 'YES') {
    // find empty line where header comment block probably ends and split file there
    let emptyLineIndex = fileLines.findIndex((line) => line.trim() === '');
    if (emptyLineIndex === -1) {
      // no empty lines found, fall back to assuming there's no header comment
      emptyLineIndex = 0;
    } else {
      // account for the empty line we found to cut it out of the content string
      emptyLineIndex += 1;
    }
    currDocs = fileLines.slice(0, emptyLineIndex).join('\n');
    isolatedContent = fileLines.slice(emptyLineIndex).join('\n');
  } else {
    // no current docs to update; whole file is code content
    isolatedContent = fileLines.join('\n');
  }

  // update docs, or write new ones if currDocs is empty/undefined
  // TODO: verify that old inaccurate docs dont influence new docs
  // TODO: experiment performance qulaity on dif types of file header comments:
  //      (1. update own comment 2. write from scratch 3. update existing generic informational header 4. fix slightly incorrect header 5. shebang)
  // TODO: what to do about file/function too long for conetxt? (rolling summarize first before asking for docs??)
  // TODO: try limiting to 2-3 sentences? max tokens?

  const docsPrompt = dedent(
    `Write a brief overview of the general purpose of this code file; refrain from documenting specifics, focus on the greater purpose of the file.

    ===
    ${isolatedContent}
    ===
    `,
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
  if (currDocs) {
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
              ${currDocs}
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

  // convert to comment in the file's language
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

  // separate new docs from content w/ an empty line to make sure we
  // maintain our assumption about the header comment ending on empty line
  return `${updatedDocsComment.trim()}\n\n${isolatedContent}`;
}
