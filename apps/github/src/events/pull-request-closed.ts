import { logEvent } from "@eave-fyi/eave-stdlib-ts/src/analytics.js";
import { Status } from "@eave-fyi/eave-stdlib-ts/src/core-api/models/github-documents.js";
import { Team } from "@eave-fyi/eave-stdlib-ts/src/core-api/models/team.js";
import {
  GetGithubDocumentsOperation,
  UpdateGithubDocumentOperation,
} from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/github-documents.js";
import { GetGithubReposOperation } from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/github-repos.js";
import { updateDocumentation } from "@eave-fyi/eave-stdlib-ts/src/function-documenting.js";
import { FileChange } from "@eave-fyi/eave-stdlib-ts/src/github-api/models.js";
import { eaveLogger } from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import { isSupportedProgrammingLanguage } from "@eave-fyi/eave-stdlib-ts/src/programming-langs/language-mapping.js";
import { CtxArg } from "@eave-fyi/eave-stdlib-ts/src/requests.js";
import { OpenAIModel } from "@eave-fyi/eave-stdlib-ts/src/transformer-ai/models.js";
import OpenAIClient, {
  formatprompt,
} from "@eave-fyi/eave-stdlib-ts/src/transformer-ai/openai.js";
import { assertPresence } from "@eave-fyi/eave-stdlib-ts/src/util.js";
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
import { EventHandlerArgs } from "../types.js";

/**
 * Handles GitHub pull request events. If the event indicates that a pull request has been closed,
 * the function logs the event and updates the status of associated documents.
 * If the pull request was merged, the function also fetches all files from the pull request,
 * determines which files need documentation, and updates the documentation in each file.
 * Finally, it creates a new pull request with the updated documentation.
 * https://docs.github.com/en/webhooks-and-events/webhooks/webhook-events-and-payloads?actionType=closed#pull_request
 *
 * @param {PullRequestEvent} event - The pull request event from GitHub.
 * @param {GitHubOperationsContext} context - The context for GitHub operations, including the Octokit instance and the current context.
 * @throws {Error} If there is an error fetching file content or creating a pull request.
 */
export default async function handler({
  event,
  ctx,
  octokit,
  eaveTeam,
}: EventHandlerArgs & {
  event: PullRequestEvent;
}) {
  if (event.action !== "closed") {
    return;
  }
  eaveLogger.debug("Processing github pull_request event", ctx);
  const repoOwner = event.repository.owner.login;
  const repoName = event.repository.name;
  const repoId = event.repository.node_id.toString();

  // don't open more docs PRs from other Eave PRs getting merged
  if (
    event.pull_request.user.type === "Bot" &&
    event.pull_request.user.login.toLowerCase().match("^eave-fyi.*?\\[bot\\]$")
  ) {
    const interaction = event.pull_request.merged
      ? Status.PR_MERGED
      : Status.PR_CLOSED;
    if (interaction === Status.PR_MERGED) {
      await logEvent(
        {
          event_name: "github_eave_pr_merged",
          event_description: `A GitHub PR opened by Eave was merged`,
          event_source: "github webhook pull_request event",
          opaque_params: { interaction },
        },
        ctx,
      );
    } else {
      await logEvent(
        {
          event_name: "github_eave_pr_closed",
          event_description: `A GitHub PR opened by Eave was closed without merging changes`,
          event_source: "github webhook pull_request event",
          opaque_params: { interaction },
        },
        ctx,
      );
    }

    await updateDocsPullRequestStatus({
      repoId,
      prNumber: event.pull_request.number,
      eaveTeam,
      ctx,
      status: interaction,
    });

    return;
  }

  // proceed only if PR commits were merged
  if (!event.pull_request.merged) {
    return;
  }

  const openaiClient = await OpenAIClient.getAuthedClient();

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

  eaveLogger.debug("file paths", ctx, { repoId, filePaths });

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

    eaveLogger.debug("creating pull request for inline code docs", ctx, {
      repoId,
      pull_request_number: event.pull_request.number,
    });

    await prCreator.createPullRequest({
      branchName: `refs/heads/eave/auto-docs/${event.pull_request.number}`,
      commitMessage: "docs: automated update",
      fileChanges: { additions: fileChanges },
      prTitle: `docs: Eave inline code documentation update for #${event.pull_request.number}`,
      prBody: `Your new code docs based on changes from PR #${event.pull_request.number}`,
    });
  } catch (e: any) {
    eaveLogger.exception(e, ctx);
    return;
  }
}

async function updateDocsPullRequestStatus({
  ctx,
  eaveTeam,
  repoId,
  prNumber,
  status,
}: {
  status: Status;
  eaveTeam: Team;
  repoId: string;
  prNumber: number;
} & CtxArg) {
  const eaveRepoResponse = await GetGithubReposOperation.perform({
    ctx,
    origin: appConfig.eaveOrigin,
    teamId: eaveTeam.id,
    input: {
      repos: [
        {
          external_repo_id: repoId,
        },
      ],
    },
  });

  const eaveRepo = eaveRepoResponse.repos[0];
  assertPresence(eaveRepo);

  try {
    const associatedGithubDocuments = await GetGithubDocumentsOperation.perform(
      {
        origin: appConfig.eaveOrigin,
        ctx,
        teamId: eaveTeam.id,
        input: {
          query_params: {
            github_repo_id: eaveRepo.id,
            pull_request_number: prNumber,
          },
        },
      },
    );

    for (const document of associatedGithubDocuments.documents) {
      await UpdateGithubDocumentOperation.perform({
        origin: appConfig.eaveOrigin,
        ctx,
        teamId: eaveTeam.id,
        input: {
          document: {
            id: document.id,
            new_values: {
              status,
            },
          },
        },
      });
    }
  } catch (e: any) {
    eaveLogger.exception(e, ctx);
    // Allow the function to continue running
  }
}
