import { logEvent } from "@eave-fyi/eave-stdlib-ts/src/analytics.js";
import { updateDocumentation } from "@eave-fyi/eave-stdlib-ts/src/function-documenting.js";
import { FileChange } from "@eave-fyi/eave-stdlib-ts/src/github-api/models.js";
import { eaveLogger } from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import { isSupportedProgrammingLanguage } from "@eave-fyi/eave-stdlib-ts/src/programming-langs/language-mapping.js";
import { OpenAIModel } from "@eave-fyi/eave-stdlib-ts/src/transformer-ai/models.js";
import OpenAIClient, {
  formatprompt,
} from "@eave-fyi/eave-stdlib-ts/src/transformer-ai/openai.js";
import {
  Blob,
  PullRequest,
  PullRequestChangedFile,
  PullRequestChangedFileConnection,
  Query,
  Repository,
  Scalars,
} from "@octokit/graphql-schema";
import { PullRequestEvent } from "@octokit/webhooks-types";
import path from "path";
import { appConfig } from "../config.js";
import * as GraphQLUtil from "../lib/graphql-util.js";
import { PullRequestCreator } from "../lib/pull-request-creator.js";
import { GitHubOperationsContext } from "../types.js";

/**
 * Receives github webhook pull_request events.
 * https://docs.github.com/en/webhooks-and-events/webhooks/webhook-events-and-payloads?actionType=closed#pull_request
 *
 * Features:
 * Checks if closed PR was merged. If so, update inline file docs
 * for each file with code changes.
 */
export default async function handler(
  event: PullRequestEvent,
  context: GitHubOperationsContext,
) {
  if (event.action !== "closed") {
    return;
  }
  const { ctx, octokit } = context;

  // don't open more docs PRs from other Eave PRs getting merged
  if (event.sender.id.toString() === (await appConfig.eaveGithubAppId)) {
    const interaction = event.pull_request.merged ? "merged" : "closed";
    await logEvent(
      {
        event_name: "github_eave_pr_interaction",
        event_description: `A GitHub PR opened by Eave was ${interaction}`,
        event_source: "github webhook pull_request event",
        opaque_params: { interaction },
      },
      ctx,
    );
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
  eaveLogger.debug("Processing github pull_request event", ctx);

  let keepPaginating = true;
  let filePaths: Array<string> = [];
  const filesQuery = await GraphQLUtil.loadQuery("getFilesInPullRequest");
  const filesQueryVariables: {
    repoOwner: Scalars["String"]["input"];
    repoName: Scalars["String"]["input"];
    prNumber: Scalars["Int"]["input"];
    batchSize: Scalars["Int"]["input"];
    after?: Scalars["String"]["input"];
  } = {
    repoOwner,
    repoName,
    prNumber: event.pull_request.number,
    batchSize: 50, // max 100
  };

  // paginate to collect all files from the PR
  while (keepPaginating) {
    const queryResp = await octokit.graphql<{
      repository: Query["repository"];
    }>(filesQuery, filesQueryVariables);
    const prRepo = <Repository>queryResp.repository;
    const pr = <PullRequest>prRepo.pullRequest;
    const prFilesConnection = <PullRequestChangedFileConnection>pr.files;
    const prFileNodes = <Array<PullRequestChangedFile>>prFilesConnection.nodes;

    if (!prFileNodes) {
      eaveLogger.error(
        "Failed to acquire file list from PR while processing PR merge event",
        ctx,
      );
      return;
    }

    const documentableFiles: Array<PullRequestChangedFile> = [];
    for (const f of prFileNodes) {
      // dont document files that aren't new or modified
      if (!(f.changeType === "ADDED" || f.changeType === "MODIFIED")) {
        continue;
      }

      // filter file types that arent source files we support writing docs for
      if (!isSupportedProgrammingLanguage(path.extname(f.path))) {
        continue;
      }

      // TODO: would we get ratelimited if we tried to do all gpt prompts in parallel after all file paths obtained?
      // TODO: test feature behavior allowing test files to be documented. Should we allow that?
      const prompt = formatprompt(`
        Given a file path, determine whether that file typically needs function-level code comments.
        Respond with only YES, or NO. Generated and test files do not need documentation.

        src/main.c: YES
        README.md: NO
        scripts/setup.sh: NO
        bin/run: NO
        frontend/tests/LogicTests.js: NO
        ${f.path}:`);
      const openaiResponse = await openaiClient.createChatCompletion({
        parameters: {
          messages: [{ role: "user", content: prompt }],
          model: OpenAIModel.GPT4,
          max_tokens: 10,
        },
        ctx,
      });

      if (openaiResponse.trim() === "YES") {
        documentableFiles.push(f);
      }
    }

    filePaths = filePaths.concat(documentableFiles.map((f) => f.path));

    // assign query vars `after` field so that next query will continue paginating
    // files where the previous request left off
    filesQueryVariables.after =
      prFilesConnection.pageInfo.endCursor || undefined; // convert null to undefined for happy types
    keepPaginating = prFilesConnection.pageInfo.hasNextPage;
  }

  // update docs in each file
  const contentsQuery = await GraphQLUtil.loadQuery("getFileContentsByPath");
  const b64UpdatedContent = await Promise.all(
    filePaths.map(async (fpath): Promise<string | null> => {
      const contentsQueryVariables: {
        repoOwner: Scalars["String"]["input"];
        repoName: Scalars["String"]["input"];
        expression: Scalars["String"]["input"];
      } = {
        repoOwner,
        repoName,
        expression: `${event.pull_request.base.ref}:${fpath}`,
      };

      const response = await octokit.graphql<{
        repository: Query["repository"];
      }>(contentsQuery, contentsQueryVariables);
      const objectRepository = <Repository>response.repository;
      const gitObject = <Blob>objectRepository?.object;
      const fileContent = gitObject?.text;
      if (!fileContent) {
        eaveLogger.error(
          `Error fetching file content in ${repoOwner}/${repoName}`,
          ctx,
        );
        return null; // exits just this iteration of map
      }

      const updatedFileContent = await updateDocumentation({
        currContent: fileContent,
        filePath: fpath,
        openaiClient,
        ctx,
        fileNodeId: gitObject.id,
      });
      if (!updatedFileContent) {
        return null;
      }

      // encode new content as b64 bcus thats how github likes it
      return Buffer.from(updatedFileContent!).toString("base64");
    }),
  );

  try {
    const fileChanges = filePaths.reduce((acc, fpath, i) => {
      const content = b64UpdatedContent[i];
      // remove entries w/ null content from content fetch failures
      if (content) {
        acc.push({
          path: fpath,
          contents: content,
        });
      }
      return acc;
    }, Array<FileChange>());

    const prCreator = new PullRequestCreator({
      repoName,
      repoOwner,
      repoId,
      baseBranchName: event.pull_request.base.ref,
      octokit,
      ctx,
    });
    await prCreator.createPullRequest({
      branchName: `refs/heads/eave/auto-docs/${event.pull_request.number}`,
      commitMessage: "docs: automated update",
      fileChanges: { additions: fileChanges },
      prTitle: "docs: Eave inline code documentation update",
      prBody: `Your new code docs based on changes from PR #${event.pull_request.number}`,
    });
  } catch (error: any) {
    eaveLogger.error(
      `GitHub API threw an error during inline docs PR creation: ${JSON.stringify(
        error,
      )}`,
      ctx,
    );
    return;
  }
}
