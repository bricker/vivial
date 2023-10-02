import { logEvent } from "@eave-fyi/eave-stdlib-ts/src/analytics.js";
import {
  DocumentType,
  GithubDocument,
  GithubDocumentValuesInput,
  Status,
} from "@eave-fyi/eave-stdlib-ts/src/core-api/models/github-documents.js";
import {
  GithubRepo,
  State,
} from "@eave-fyi/eave-stdlib-ts/src/core-api/models/github-repos.js";
import { Team } from "@eave-fyi/eave-stdlib-ts/src/core-api/models/team.js";
import {
  CreateGithubDocumentOperation,
  GetGithubDocumentsOperation,
  UpdateGithubDocumentOperation,
} from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/github-documents.js";
import { GetGithubReposOperation } from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/github-repos.js";
import { GetTeamOperation } from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/team.js";
import { MissingRequiredHeaderError } from "@eave-fyi/eave-stdlib-ts/src/exceptions.js";
import { RunApiDocumentationTaskRequestBody } from "@eave-fyi/eave-stdlib-ts/src/github-api/operations/run-api-documentation-task.js";
import { EAVE_TEAM_ID_HEADER } from "@eave-fyi/eave-stdlib-ts/src/headers.js";
import {
  LogContext,
  eaveLogger,
} from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import { CtxArg } from "@eave-fyi/eave-stdlib-ts/src/requests.js";
import { Blob, FileAddition, FileChanges, Maybe, Query, Repository, Scalars, Tree, TreeEntry } from "@octokit/graphql-schema";
import assert, { AssertionError } from "assert";
import Express from "express";
import { appConfig } from "../config.js";
import { loadQuery } from "../lib/graphql-util.js";
import { createOctokitClient, getInstallationId } from "../lib/octokit-util.js";
import { PullRequestCreator } from "../lib/pull-request-creator.js";
import { GitHubOperationsContext } from "../types.js";
import { components } from "@octokit/openapi-types";
import { ProgrammingLanguage, getProgrammingLanguageByExtension, getProgrammingLanguageByFilePathOrName } from "@eave-fyi/eave-stdlib-ts/src/programming-langs/language-mapping.js";
import Parser from "tree-sitter";
import { ExpressAPI, ExpressParsingUtility } from "@eave-fyi/eave-stdlib-ts/src/api-documenting/express-parsing-utility.js";
import { CodeFile } from "@eave-fyi/eave-stdlib-ts/src/api-documenting/parsing-utility.js";
import path from "path";
import { FileChange } from "@eave-fyi/eave-stdlib-ts/src/github-api/models.js";
import { assertPresence, underscoreify } from "@eave-fyi/eave-stdlib-ts/src/util.js";

const IGNORE_DIRS = [
  "node_modules",
];

export async function runApiDocumentationTaskHandler(
  req: Express.Request,
  res: Express.Response,
): Promise<void> {
  const ctx = LogContext.load(res);
  const input = <RunApiDocumentationTaskRequestBody>req.body;

  const teamId = req.header(EAVE_TEAM_ID_HEADER);
  if (!teamId) {
    throw new MissingRequiredHeaderError(EAVE_TEAM_ID_HEADER);
  }

  const team = await getTeam({ teamId, ctx });
  const installId = await getInstallationId(team.id, ctx);
  assert(installId, `No github integration found for team ID ${team.id}`);

  const octokit = await createOctokitClient(installId);

  const repo = await getRepo({ team, input, ctx });
  assert(
    repo.api_documentation_state === State.ENABLED,
    `API documentation feature not enabled for repo ID ${repo.external_repo_id}`,
  );

  await logEvent({
    event_name: "run_api_documentation",
    event_description:
      "The API documentation process was kicked off for a repo",
    eave_team: team,
    event_source: "github app",
    opaque_params: {
      repo,
    },
  }, ctx);

  const externalRepo = await getExternalRepo({ repo, octokit, ctx });

  const parser = new ExpressParsingUtility({ ctx });

  const fwdArgs = { repo: externalRepo, octokit, ctx, parser };

  const expressApiRootDirs = await getExpressAPIRootDirs({ repo: externalRepo, parser, octokit, ctx });

  if (expressApiRootDirs.length === 0) {
    await logEvent({
      event_name: "express_api_detection_no_apps_detected",
      event_description:
        "The API documentation feature is enabled for this repository, but no express apps were not detected.",
      eave_team: team,
      event_source: "github app",
      opaque_params: {
        repo,
      },
    }, ctx);

    eaveLogger.warning("No express apps found", repo, ctx);
    res.sendStatus(200);
    return;
  }

  const existingEaveDocs = await getExistingGithubDocuments({ repo, team, ctx });

  const results = await Promise.allSettled(expressApiRootDirs.map(async (rootDir) => {
    const apiInfo = await getExpressApiInfo({ rootDir, team, eaveRepo: repo, ...fwdArgs });
    assertPresence(apiInfo);
    assertPresence(apiInfo.rootFile);

    let eaveDoc = existingEaveDocs.find((d) => d.file_path === apiInfo.documentationFilePath);
    if (eaveDoc) {
      eaveDoc = await updateGithubDocument({ team, ctx, document: eaveDoc, newValues: { api_name: apiInfo.name, file_path: apiInfo.documentationFilePath, status: Status.PROCESSING } });
    } else {
      eaveDoc = await createPlaceholderGithubDocument({ apiInfo, repo, team, ctx });
    }

    const endpoints = await getExpressAPIEndpoints({ apiRootFilePath: apiInfo.rootFile.path, ...fwdArgs });
    if (!endpoints || endpoints.length === 0) {
      await logEvent({
        event_name: "express_api_detection_no_endpoints",
        event_description:
          "An express API was detected, but no endpoints were found.",
        eave_team: team,
        event_source: "github app",
        opaque_params: {
          repo,
          externalRepo,
          rootDir,
          expressApiRootFile: apiInfo.rootFile.path,
          language: apiInfo.rootFile.language,
          apiName: apiInfo.name,
        },
      }, ctx);

      eaveLogger.warning("No express API endpoints found", { rootDir, expressApiRootFile: apiInfo.rootFile.path, apiName: apiInfo.name }, repo, externalRepo, ctx);
      await updateGithubDocument({ team, ctx, document: eaveDoc, newValues: { status: Status.FAILED } });
      return Promise.reject();
    }

    apiInfo.endpoints = endpoints;

    const newDocumentContents = await parser.generateExpressAPIDoc({ api: apiInfo, ctx});
    if (!newDocumentContents) {
      await logEvent({
        event_name: "express_api_documentation_not_generated",
        event_description:
          "Documentation for an express API was not generated, so the resulting document was empty. No pull request will be opened.",
        eave_team: team,
        event_source: "github app",
        opaque_params: {
          repo,
          externalRepo,
          rootDir,
          expressApiRootFile: apiInfo.rootFile.path,
          language: apiInfo.rootFile.language,
          apiName: apiInfo.name,
        },
      }, ctx);
      eaveLogger.warning("Empty express API documentation.", { rootDir, expressApiRootFile: apiInfo.rootFile.path, apiName: apiInfo.name }, repo, externalRepo, ctx);

      await updateGithubDocument({ team, ctx, document: eaveDoc, newValues: { status: Status.FAILED } });
      return Promise.reject();
    } else {
      await logEvent({
        event_name: "express_api_documentation_generated",
        event_description:
          "Documentation for an express API was successfully generated.",
        eave_team: team,
        event_source: "github app",
        opaque_params: {
          repo,
          externalRepo,
          rootDir,
          expressApiRootFile: apiInfo.rootFile.path,
          language: apiInfo.rootFile.language,
          apiName: apiInfo.name,
        },
      }, ctx);
      apiInfo.documentation = newDocumentContents;
      return apiInfo;
    }
  }));

  const documents = results.filter((r) => r.status === "fulfilled").map((r) => (<PromiseFulfilledResult<ExpressAPI>>r).value);

  const fileAdditions: FileAddition[] = documents.map((d) => {
    assertPresence(d.documentation);
    assertPresence(d.documentation);
    return {
      path: d.documentationFilePath,
      contents: Buffer.from(d.documentation).toString("base64"),
    }
  });

  const prCreator = new PullRequestCreator({
    repoName: externalRepo.name,
    repoOwner: externalRepo.owner.login,
    repoId: externalRepo.id,
    baseBranchName: externalRepo.defaultBranchRef?.name || "main", // The only reason `defaultBranchRef` would be undefined is if it wasn't specified in the query fields. But defaulting to "main" is easier than handling the runtime error and will work for most cases.
    octokit,
    ctx,
  });

  const pullRequest = await prCreator.createPullRequest({
    branchName: "refs/heads/eave/auto-docs/api",
    commitMessage: "docs: automated update",
    prTitle: "docs: Eave API documentation update",
    prBody: "Your new API docs based on recent changes to your code",
    fileChanges: {
      additions: fileAdditions,
    },
  });

  for (const document of documents) {
    const eaveDoc = existingEaveDocs.find((d) => d.file_path === document.documentationFilePath);
    assertPresence(eaveDoc);
    await updateGithubDocument({
      document: eaveDoc,
      team,
      ctx,
      newValues: {
        pull_request_number: pullRequest.number,
        status: Status.PR_OPENED,
      },
    });
  }
}
