import { logEvent } from "@eave-fyi/eave-stdlib-ts/src/analytics.js";
import {
  DocumentType,
  GithubDocument,
  GithubDocumentUpdateInput,
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
import { ExpressAPI } from "@eave-fyi/eave-stdlib-ts/src/api-documenting/express-parsing-utility.js";
import { CodeFile } from "@eave-fyi/eave-stdlib-ts/src/api-documenting/parsing-utility.js";
import path from "path";
import { FileChange } from "@eave-fyi/eave-stdlib-ts/src/github-api/models.js";
import { assertPresence, underscoreify } from "@eave-fyi/eave-stdlib-ts/src/util.js";
import { CoreAPIData } from "../lib/api-documentation/core-api.js";
import { GithubAPIData } from "../lib/api-documentation/github-api.js";
import { JsonObject, JsonValue } from "@eave-fyi/eave-stdlib-ts/src/types.js";
import { ExpressAPIDocumentBuilder } from "../lib/api-documentation/builder.js";
import OpenAIClient, { formatprompt } from "@eave-fyi/eave-stdlib-ts/src/transformer-ai/openai.js";
import { OpenAIModel } from "@eave-fyi/eave-stdlib-ts/src/transformer-ai/models.js";

const IGNORE_DIRS = [
  "node_modules",
];

const ANALYTICS_SOURCE = "run api documentation cron handler";

export async function runApiDocumentationTaskHandler(
  req: Express.Request,
  res: Express.Response,
): Promise<void> {
  const ctx = LogContext.load(res);
  const input = <RunApiDocumentationTaskRequestBody>req.body;
  const sharedAnalyticsParams: {[key:string]: JsonValue} = {};

  const teamId = req.header(EAVE_TEAM_ID_HEADER);
  if (!teamId) {
    throw new MissingRequiredHeaderError(EAVE_TEAM_ID_HEADER);
  }

  const coreAPIData = await CoreAPIData.load({ teamId, ctx, eaveGithubRepoInput: input.repo });
  sharedAnalyticsParams["eaveGithubRepo"] = coreAPIData.eaveGithubRepo;
  ctx.set({ eave_team: coreAPIData.team });

  assert(
    coreAPIData.eaveGithubRepo.api_documentation_state === State.ENABLED,
    `API documentation feature not enabled for repo ID ${coreAPIData.eaveGithubRepo.external_repo_id}`,
  );

  const installId = await getInstallationId(coreAPIData.team.id, ctx);
  assert(installId, `No github integration found for team ID ${coreAPIData.team.id}`);

  const octokit = await createOctokitClient(installId);

  await logEvent({
    event_name: "run_api_documentation",
    event_description:
      "The API documentation process was kicked off for a repo",
    eave_team: coreAPIData.team,
    event_source: ANALYTICS_SOURCE,
    opaque_params: {
      ...sharedAnalyticsParams,
    },
  }, ctx);

  const githubAPIData = await GithubAPIData.load({ ctx, octokit, eaveGithubRepo: coreAPIData.eaveGithubRepo });

  if (githubAPIData.expressRootDirs.length === 0) {
    await logEvent({
      event_name: "express_api_detection_no_apps_detected",
      event_description:
        "The API documentation feature is enabled for this repository, but no express apps were not detected.",
      eave_team: coreAPIData.team,
      event_source: ANALYTICS_SOURCE,
      opaque_params: {
        ...sharedAnalyticsParams,
      },
    }, ctx);

    res.sendStatus(200);
    return;
  }

  sharedAnalyticsParams["expressRootDirs"] = githubAPIData.expressRootDirs;

  const results = await Promise.allSettled(githubAPIData.expressRootDirs.map(async (apiRootDir) => {
    const expressAPIInfo = await ExpressAPIDocumentBuilder.buildAPI({ githubAPIData, apiRootDir, ctx });
    assertPresence(expressAPIInfo);

    expressAPIInfo.documentationFilePath = documentationFilePath({ apiName: expressAPIInfo.name });
    let eaveDoc = coreAPIData.getGithubDocument({ filePath: expressAPIInfo.documentationFilePath })

    if (!expressAPIInfo.rootFile) {
      // We thought this dir contained an Express app, but couldn't find a file that initialized the express server.
      await logEvent({
        event_name: "express_api_detection_false_positive",
        event_description:
          "An express API was detected, but no root file was found.",
        event_source: ANALYTICS_SOURCE,
        opaque_params: {
          apiRootDir,
        },
      }, ctx);

      if (eaveDoc) {
        await coreAPIData.updateGithubDocument({ document: eaveDoc, newValues: { status: Status.FAILED } });
      }

      return Promise.reject();
    }

    if (!expressAPIInfo.endpoints || expressAPIInfo.endpoints.length === 0) {
      await logEvent({
        event_name: "express_api_detection_no_endpoints",
        event_description:
          "An express API was detected, but no endpoints were found.",
        event_source: ANALYTICS_SOURCE,
        opaque_params: {
          apiRootDir,
          apiRootFile: expressAPIInfo.rootFile?.asJSON,
         },
      }, ctx);

      if (eaveDoc) {
        await coreAPIData.updateGithubDocument({ document: eaveDoc, newValues: { status: Status.FAILED } });
      }

      return Promise.reject();
    }

    if (eaveDoc) {
      eaveDoc = await coreAPIData.updateGithubDocument({ document: eaveDoc, newValues: { status: Status.PROCESSING } });
    } else {
      eaveDoc = await coreAPIData.createPlaceholderGithubDocument({ apiName: expressAPIInfo.name, documentationFilePath: expressAPIInfo.documentationFilePath});
    }

    const newDocumentContents = await generateExpressAPIDoc({ expressAPIInfo, ctx});
    if (!newDocumentContents) {
      await logEvent({
        event_name: "express_api_documentation_not_generated",
        event_description:
          "Documentation for an express API was not generated, so the resulting document was empty. No pull request will be opened.",
        event_source: ANALYTICS_SOURCE,
        opaque_params: {
          expressApiRootFile: expressAPIInfo.rootFile.path,
          language: expressAPIInfo.rootFile.language,
        },
      }, ctx);
      eaveLogger.warning("Empty express API documentation.", { expressApiRootFile: expressAPIInfo.rootFile.path }, ctx);

      await coreAPIData.updateGithubDocument({ document: eaveDoc, newValues: { status: Status.FAILED } });
      return Promise.reject();
    } else {
      await logEvent({
        event_name: "express_api_documentation_generated",
        event_description:
          "Documentation for an express API was successfully generated.",
        event_source: ANALYTICS_SOURCE,
        opaque_params: {
          expressApiRootFile: expressAPIInfo.rootFile.path,
          language: expressAPIInfo.rootFile.language,
          apiName: expressAPIInfo.name,
        },
      }, ctx);

      expressAPIInfo.documentation = newDocumentContents;
      return expressAPIInfo;
    }
  }));

  const documents = results.filter((r) => r.status === "fulfilled").map((r) => (<PromiseFulfilledResult<ExpressAPI>>r).value);

  const fileAdditions: FileAddition[] = documents.map((d) => {
    assertPresence(d.documentation);

    return {
      path: d.documentationFilePath || "eave_docs.md", // TODO: This will drop it in the root of the project
      contents: Buffer.from(d.documentation).toString("base64"),
    }
  });

  if (fileAdditions.length === 0) {
    eaveLogger.warning("No file additions", ctx);
    await updateDocuments({ coreAPIData, documents, newValues: { status: Status.FAILED } });
    return;
  }

  const prCreator = new PullRequestCreator({
    repoName: githubAPIData.externalGithubRepo.name,
    repoOwner: githubAPIData.externalGithubRepo.owner.login,
    repoId: githubAPIData.externalGithubRepo.id,
    baseBranchName: githubAPIData.externalGithubRepo.defaultBranchRef?.name || "main", // The only reason `defaultBranchRef` would be undefined is if it wasn't specified in the query fields. But defaulting to "main" is easier than handling the runtime error and will work for most cases.
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

  await updateDocuments({ coreAPIData, documents, newValues: { pull_request_number: pullRequest.number, status: Status.FAILED } });
}

async function updateDocuments({ coreAPIData, documents, newValues }: { coreAPIData: CoreAPIData, documents: ExpressAPI[], newValues: GithubDocumentValuesInput }) {
  for (const document of documents) {
    if (document.documentationFilePath) {
      const eaveDoc = coreAPIData.getGithubDocument({ filePath: document.documentationFilePath })
      assertPresence(eaveDoc);
      await coreAPIData.updateGithubDocument({
        document: eaveDoc,
        newValues,
      });
    }
  }
}

/**
 * Given a list of Express API endpoints, this function builds up API
 * documentation by sending the endpoints to OpenAI one at a time.
 */
async function generateExpressAPIDoc({ expressAPIInfo, ctx }: CtxArg & { expressAPIInfo: ExpressAPI }): Promise<string | null> {
  let apiDoc = "";
  assertPresence(expressAPIInfo.endpoints);

  for (const apiEndpoint of expressAPIInfo.endpoints) {
    const openaiClient = await OpenAIClient.getAuthedClient();
    const systemPrompt = formatprompt(`
      You will be given a block of ${expressAPIInfo.rootFile?.language || ""} code, delimited by three exclamation marks, containing definitions for API endpoints using the Express API framework.

      Your task is to generate API documentation for the provided Express REST API endpoint.

      If the provided code does not contain enough information to generate API documentation, respond with "none"

      Otherwise, use the following template to format your response:

      ## {description of the API endpoint in 3 words or less}

      \`\`\`
      {HTTP Method} {Path}
      \`\`\`

      {high-level description of what the API endpoint does}

      ### Path Parameters

      **{name}** ({type}) *{optional or required}* - {description}

      ### Example Request

      \`\`\`
      {example request written in JavaScript}
      \`\`\`

      ### Example Response

      \`\`\`
      {example response}
      \`\`\`

      ### Response Codes

      **{response code}**: {explanation of when this response code will be returned}

    `);
    const userPrompt = formatprompt("!!!", apiEndpoint);

    try {
      const openaiResponse = await openaiClient.createChatCompletion({
        parameters: {
          messages: [
            { role: "system", content: systemPrompt },
            { role: "user", content: userPrompt },
          ],
          model: OpenAIModel.GPT4,
          temperature: 0,
        },
        ctx,
      });

      if (openaiResponse.length === 0 || openaiResponse.match(/^none/)) {
        await logEvent({
          event_name: "express_api_documentation_openai_empty_response",
          event_description:
            "OpenAI couldn't generate documentation for this API",
          event_source: "express parsing utility",
          opaque_params: {
            apiName: expressAPIInfo.name,
            rootDir: expressAPIInfo.rootDir,
            rootFile: expressAPIInfo.rootFile?.path,
            language: expressAPIInfo.rootFile?.language,
          },
        }, ctx);

        eaveLogger.warning("openAI didn't return API documentation", { openaiResponse }, ctx);
        continue;
      }

      apiDoc += `${openaiResponse}\n\n<br />\n\n`;
    } catch (e: any) {
      eaveLogger.exception(e, ctx);
      continue;
    }
  }

  if (apiDoc.length === 0) {
    return null;
  }
  return apiDoc;
}

function documentationFilePath({ apiName }: { apiName: string }): string {
  const basename = underscoreify(apiName);
  return `eave_docs/${basename}.md`;
}
