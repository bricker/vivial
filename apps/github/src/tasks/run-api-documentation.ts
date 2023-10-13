import { logEvent } from "@eave-fyi/eave-stdlib-ts/src/analytics.js";
import { ExpressAPI } from "@eave-fyi/eave-stdlib-ts/src/api-documenting/express-parsing-utility.js";
import {
  GithubDocumentValuesInput,
  Status,
} from "@eave-fyi/eave-stdlib-ts/src/core-api/models/github-documents.js";
import { State } from "@eave-fyi/eave-stdlib-ts/src/core-api/models/github-repos.js";
import { MissingRequiredHeaderError } from "@eave-fyi/eave-stdlib-ts/src/exceptions.js";
import { RunApiDocumentationTaskRequestBody } from "@eave-fyi/eave-stdlib-ts/src/github-api/operations/run-api-documentation-task.js";
import { EAVE_TEAM_ID_HEADER } from "@eave-fyi/eave-stdlib-ts/src/headers.js";
import {
  LogContext,
  eaveLogger,
} from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import { CtxArg } from "@eave-fyi/eave-stdlib-ts/src/requests.js";
import { OpenAIModel } from "@eave-fyi/eave-stdlib-ts/src/transformer-ai/models.js";
import OpenAIClient, {
  formatprompt,
} from "@eave-fyi/eave-stdlib-ts/src/transformer-ai/openai.js";
import { JsonValue } from "@eave-fyi/eave-stdlib-ts/src/types.js";
import {
  assertPresence,
  underscoreify,
} from "@eave-fyi/eave-stdlib-ts/src/util.js";
import { FileAddition } from "@octokit/graphql-schema";
import assert from "assert";
import Express from "express";
import { ExpressAPIDocumentBuilder } from "../lib/api-documentation/builder.js";
import { CoreAPIData } from "../lib/api-documentation/core-api.js";
import { GithubAPIData } from "../lib/api-documentation/github-api.js";
import { createOctokitClient, getInstallationId } from "../lib/octokit-util.js";
import { PullRequestCreator } from "../lib/pull-request-creator.js";

const ANALYTICS_SOURCE = "run api documentation cron handler";

/**
 * Handles the task of running API documentation. It loads the necessary context and input data, validates the team ID,
 * and loads the core API data. It then checks the state of the API documentation, retrieves the installation ID, and creates
 * an Octokit client. It logs the event of running the API documentation and loads the Github API data. If no express apps
 * are detected, it logs a warning and sends a 200 status response. If express apps are detected, it builds the API documentation
 * for each app, generates the API documentation from OpenAI, and creates or updates the Github document accordingly. It then
 * creates a pull request with the new or updated documentation.
 *
 * @param {Express.Request} req - The request object.
 * @param {Express.Response} res - The response object.
 * @returns {Promise<void>} - A promise that resolves when the function has completed.
 * @throws {MissingRequiredHeaderError} - If the team ID header is missing.
 * @throws {Error} - If the API documentation state is not enabled, no Github integration is found for the team ID,
 *                    no express apps are detected, no root file is found, no express endpoints are found, or the API documentation
 *                    is not generated.
 */
export async function runApiDocumentationTaskHandler(
  req: Express.Request,
  res: Express.Response,
): Promise<void> {
  const ctx = LogContext.load(res);
  ctx.feature_name = "api_documentation";
  eaveLogger.debug("API documentation task started", { input: req.body }, ctx);

  const input = <RunApiDocumentationTaskRequestBody>req.body;
  const sharedAnalyticsParams: { [key: string]: JsonValue } = {};

  const teamId = req.header(EAVE_TEAM_ID_HEADER);
  if (!teamId) {
    throw new MissingRequiredHeaderError(EAVE_TEAM_ID_HEADER);
  }

  const coreAPIData = await CoreAPIData.load({
    teamId,
    ctx,
    eaveGithubRepoInput: input.repo,
  });
  sharedAnalyticsParams["core_api_data"] = coreAPIData.logParams;
  ctx.set({ eave_team: coreAPIData.team });

  eaveLogger.debug("eave core API data", sharedAnalyticsParams, ctx);

  assert(
    coreAPIData.eaveGithubRepo.api_documentation_state === State.ENABLED,
    `API documentation feature not enabled for repo ID ${coreAPIData.eaveGithubRepo.external_repo_id}`,
  );

  const installId = await getInstallationId(coreAPIData.team.id, ctx);
  assert(
    installId,
    `No github integration found for team ID ${coreAPIData.team.id}`,
  );

  const octokit = await createOctokitClient(installId);

  await logEvent(
    {
      event_name: "run_api_documentation",
      event_description:
        "The API documentation process was kicked off for a repo",
      eave_team: coreAPIData.team,
      event_source: ANALYTICS_SOURCE,
      opaque_params: {
        ...sharedAnalyticsParams,
      },
    },
    ctx,
  );

  const githubAPIData = await GithubAPIData.load({
    ctx,
    octokit,
    eaveGithubRepo: coreAPIData.eaveGithubRepo,
  });
  sharedAnalyticsParams["github_data"] = githubAPIData.logParams;

  if (githubAPIData.expressRootDirs.length === 0) {
    eaveLogger.warning("no express apps detected", sharedAnalyticsParams, ctx);

    await logEvent(
      {
        event_name: "express_api_detection_no_apps_detected",
        event_description:
          "The API documentation feature is enabled for this repository, but no express apps were detected.",
        eave_team: coreAPIData.team,
        event_source: ANALYTICS_SOURCE,
        opaque_params: {
          ...sharedAnalyticsParams,
        },
      },
      ctx,
    );

    res.sendStatus(200);
    return;
  }

  eaveLogger.debug("express apps detected", sharedAnalyticsParams, ctx);

  const results = await Promise.allSettled(
    githubAPIData.expressRootDirs.map(async (apiRootDir) => {
      try {
        const localAnalyticsParams: { [key: string]: JsonValue } = {};
        localAnalyticsParams["api_root_dir"] = apiRootDir;

        eaveLogger.debug(
          "building documentation",
          localAnalyticsParams,
          sharedAnalyticsParams,
          ctx,
        );

        const expressAPIInfo = await ExpressAPIDocumentBuilder.buildAPI({
          githubAPIData,
          apiRootDir,
          ctx,
        });
        assertPresence(expressAPIInfo);

        expressAPIInfo.documentationFilePath = documentationFilePath({
          apiName: expressAPIInfo.name,
        });

        localAnalyticsParams["express_api_info"] = expressAPIInfo.asJSON;
        eaveLogger.debug(
          "express API info",
          localAnalyticsParams,
          sharedAnalyticsParams,
          ctx,
        );

        let eaveDoc = coreAPIData.getGithubDocument({
          filePath: expressAPIInfo.documentationFilePath,
        });
        localAnalyticsParams["eave_doc"] = eaveDoc;
        eaveLogger.debug(
          "existing eave doc",
          localAnalyticsParams,
          sharedAnalyticsParams,
          ctx,
        );

        if (!expressAPIInfo.rootFile) {
          eaveLogger.warning(
            "no root file found",
            localAnalyticsParams,
            sharedAnalyticsParams,
            ctx,
          );

          // We thought this dir contained an Express app, but couldn't find a file that initialized the express server.
          await logEvent(
            {
              event_name: "express_api_detection_false_positive",
              event_description:
                "An express API was detected, but no root file was found.",
              event_source: ANALYTICS_SOURCE,
              opaque_params: {
                ...localAnalyticsParams,
                ...sharedAnalyticsParams,
              },
            },
            ctx,
          );

          if (eaveDoc) {
            eaveLogger.warning(
              "updating github document with status FAILED",
              localAnalyticsParams,
              sharedAnalyticsParams,
              ctx,
            );

            await coreAPIData.updateGithubDocument({
              document: eaveDoc,
              newValues: { status: Status.FAILED },
            });
          }

          return null;
        }

        if (
          !expressAPIInfo.endpoints ||
          expressAPIInfo.endpoints.length === 0
        ) {
          eaveLogger.warning(
            "no express endpoints found",
            sharedAnalyticsParams,
            localAnalyticsParams,
            ctx,
          );

          await logEvent(
            {
              event_name: "express_api_detection_no_endpoints",
              event_description:
                "An express API was detected, but no endpoints were found.",
              event_source: ANALYTICS_SOURCE,
              opaque_params: {
                ...sharedAnalyticsParams,
                ...localAnalyticsParams,
              },
            },
            ctx,
          );

          if (eaveDoc) {
            eaveLogger.warning(
              "updating github document with status FAILED",
              sharedAnalyticsParams,
              localAnalyticsParams,
              ctx,
            );

            await coreAPIData.updateGithubDocument({
              document: eaveDoc,
              newValues: { status: Status.FAILED },
            });
          }

          return null;
        }

        if (eaveDoc) {
          eaveLogger.debug(
            "updating github document with status PROCESSING",
            sharedAnalyticsParams,
            localAnalyticsParams,
            ctx,
          );

          eaveDoc = await coreAPIData.updateGithubDocument({
            document: eaveDoc,
            newValues: { status: Status.PROCESSING },
          });
          localAnalyticsParams["eave_doc"] = eaveDoc;
        } else {
          eaveLogger.debug(
            "creating initial placeholder github document",
            sharedAnalyticsParams,
            localAnalyticsParams,
            ctx,
          );
          eaveDoc = await coreAPIData.createPlaceholderGithubDocument({
            apiName: expressAPIInfo.name,
            documentationFilePath: expressAPIInfo.documentationFilePath,
          });
          localAnalyticsParams["eave_doc"] = eaveDoc;
        }

        eaveLogger.debug(
          "generating API documentation from openai",
          sharedAnalyticsParams,
          localAnalyticsParams,
          ctx,
        );

        const newDocumentContents = await generateExpressAPIDoc({
          expressAPIInfo,
          ctx,
        });
        if (!newDocumentContents) {
          await logEvent(
            {
              event_name: "express_api_documentation_not_generated",
              event_description:
                "Documentation for an express API was not generated, so the resulting document was empty. No pull request will be opened.",
              event_source: ANALYTICS_SOURCE,
              opaque_params: {
                ...sharedAnalyticsParams,
                ...localAnalyticsParams,
              },
            },
            ctx,
          );
          eaveLogger.warning(
            "Empty express API documentation.",
            sharedAnalyticsParams,
            localAnalyticsParams,
            ctx,
          );

          eaveLogger.warning(
            "updating github document with status FAILED",
            sharedAnalyticsParams,
            localAnalyticsParams,
            ctx,
          );

          await coreAPIData.updateGithubDocument({
            document: eaveDoc,
            newValues: { status: Status.FAILED },
          });

          return null;
        }

        await logEvent(
          {
            event_name: "express_api_documentation_generated",
            event_description:
              "Documentation for an express API was successfully generated.",
            event_source: ANALYTICS_SOURCE,
            opaque_params: {
              ...sharedAnalyticsParams,
              ...localAnalyticsParams,
            },
          },
          ctx,
        );
        eaveLogger.debug(
          "successfully generated API documentation",
          sharedAnalyticsParams,
          localAnalyticsParams,
          ctx,
        );

        expressAPIInfo.documentation = newDocumentContents;
        return expressAPIInfo;
      } catch (e: any) {
        eaveLogger.exception(e, sharedAnalyticsParams, ctx);
        throw e;
      }
    }),
  );

  eaveLogger.debug(
    "api doc generate promise results",
    {
      results: results.map((r) => ({
        status: r.status,
        fulfilledValue: r.status === "fulfilled" ? r.value?.asJSON : undefined,
        rejectedReason: r.status === "rejected" ? r.reason : undefined,
      })),
    },
    sharedAnalyticsParams,
    ctx,
  );

  const validExpressAPIs = results
    .filter((r) => r.status === "fulfilled" && r.value)
    .map((r) => (<PromiseFulfilledResult<ExpressAPI>>r).value);
  sharedAnalyticsParams["express_apis"] = validExpressAPIs.map((e) => e.asJSON);
  eaveLogger.debug("final express APIs", sharedAnalyticsParams, ctx);

  const fileAdditions: FileAddition[] = validExpressAPIs.map((d) => {
    assertPresence(d.documentation);

    return {
      path: d.documentationFilePath || "eave_docs.md", // TODO: This will drop it in the root of the project
      contents: Buffer.from(d.documentation).toString("base64"),
    };
  });

  if (fileAdditions.length === 0) {
    eaveLogger.warning("No file additions", sharedAnalyticsParams, ctx);
    eaveLogger.warning(
      "updating github documents with status FAILED",
      sharedAnalyticsParams,
      ctx,
    );
    await updateDocuments({
      coreAPIData,
      expressAPIs: validExpressAPIs,
      newValues: { status: Status.FAILED },
    });
    return;
  }

  const prCreator = new PullRequestCreator({
    repoName: githubAPIData.externalGithubRepo.name,
    repoOwner: githubAPIData.externalGithubRepo.owner.login,
    repoId: githubAPIData.externalGithubRepo.id,
    baseBranchName:
      githubAPIData.externalGithubRepo.defaultBranchRef?.name || "main", // The only reason `defaultBranchRef` would be undefined is if it wasn't specified in the query fields. But defaulting to "main" is easier than handling the runtime error and will work for most cases.
    octokit,
    ctx,
  });

  eaveLogger.debug("creating pull request", sharedAnalyticsParams, ctx);

  const pullRequest = await prCreator.createPullRequest({
    branchName: "refs/heads/eave/auto-docs/api",
    commitMessage: "docs: automated update",
    prTitle: "docs: Eave API documentation update",
    prBody: "Your new API docs based on recent changes to your code",
    fileChanges: {
      additions: fileAdditions,
    },
  });

  await updateDocuments({
    coreAPIData,
    expressAPIs: validExpressAPIs,
    newValues: {
      pull_request_number: pullRequest.number,
      status: Status.PR_OPENED,
    },
  });
}

/**
 * Updates the documentation of Express APIs using the provided new values.
 *
 * @async
 * @param {Object} params - The parameters for updating documents.
 * @param {CoreAPIData} params.coreAPIData - The Core API data instance.
 * @param {ExpressAPI[]} params.expressAPIs - An array of Express APIs whose documentation needs to be updated.
 * @param {GithubDocumentValuesInput} params.newValues - The new values to be updated in the documentation.
 *
 * @throws {Error} If the documentation for an Express API is not found.
 *
 * @returns {Promise<void>} A promise that resolves when all document updates have been completed.
 */
async function updateDocuments({
  coreAPIData,
  expressAPIs,
  newValues,
}: {
  coreAPIData: CoreAPIData;
  expressAPIs: ExpressAPI[];
  newValues: GithubDocumentValuesInput;
}) {
  for (const expressAPI of expressAPIs) {
    if (expressAPI.documentationFilePath) {
      const eaveDoc = coreAPIData.getGithubDocument({
        filePath: expressAPI.documentationFilePath,
      });
      assertPresence(eaveDoc);
      await coreAPIData.updateGithubDocument({
        document: eaveDoc,
        newValues,
      });
    }
  }
}

/**
 * Generates API documentation for the provided Express REST API endpoints by sending the endpoints to OpenAI one at a time.
 *
 * @param {Object} args - The arguments object.
 * @param {Object} args.expressAPIInfo - Information about the Express API.
 * @param {Object} args.ctx - The context object.
 * @returns {Promise<string|null>} The generated API documentation or null if no documentation could be generated.
 *
 * @throws Will throw an error if the OpenAI client fails to generate the documentation.
 */
async function generateExpressAPIDoc({
  expressAPIInfo,
  ctx,
}: CtxArg & { expressAPIInfo: ExpressAPI }): Promise<string | null> {
  let apiDoc = "";
  assertPresence(expressAPIInfo.endpoints);

  for (const apiEndpoint of expressAPIInfo.endpoints) {
    const openaiClient = await OpenAIClient.getAuthedClient();
    const systemPrompt = formatprompt(`
      You will be given a block of ${
        expressAPIInfo.rootFile?.language || ""
      } code, delimited by three exclamation marks, containing definitions for API endpoints using the Express API framework.

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
        await logEvent(
          {
            event_name: "express_api_documentation_openai_empty_response",
            event_description:
              "OpenAI couldn't generate documentation for an API Endpoint",
            event_source: "express parsing utility",
            opaque_params: {
              apiName: expressAPIInfo.name,
              rootDir: expressAPIInfo.rootDir,
              rootFile: expressAPIInfo.rootFile?.path,
              language: expressAPIInfo.rootFile?.language,
            },
          },
          ctx,
        );

        eaveLogger.warning(
          "openAI didn't return API documentation",
          { express_api_info: expressAPIInfo.asJSON },
          ctx,
        );
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

/**
 * Generates the file path for the documentation of a given API.
 *
 * @param {Object} options - The options object.
 * @param {string} options.apiName - The name of the API.
 * @returns {string} The file path for the API's documentation.
 */
function documentationFilePath({ apiName }: { apiName: string }): string {
  const basename = underscoreify(apiName);
  return `eave_docs/${basename}.md`;
}
