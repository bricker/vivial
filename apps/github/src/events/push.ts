import { logEvent } from "@eave-fyi/eave-stdlib-ts/src/analytics.js";
import { DocumentInput } from "@eave-fyi/eave-stdlib-ts/src/core-api/models/documents.js";
import {
  SubscriptionSourceEvent,
  SubscriptionSourcePlatform,
} from "@eave-fyi/eave-stdlib-ts/src/core-api/models/subscriptions.js";
import { UpsertDocumentOperation } from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/documents.js";
import { GetGithubInstallationOperation } from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/github.js";
import {
  GetSubscriptionOperation,
  GetSubscriptionResponseBody,
} from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/subscriptions.js";
import { eaveLogger } from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import { OpenAIModel } from "@eave-fyi/eave-stdlib-ts/src/transformer-ai/models.js";
import OpenAIClient from "@eave-fyi/eave-stdlib-ts/src/transformer-ai/openai.js";
import { rollingSummary } from "@eave-fyi/eave-stdlib-ts/src/transformer-ai/util.js";
import {
  Blob,
  Commit,
  Query,
  Repository,
  Scalars,
  TreeEntry,
} from "@octokit/graphql-schema";
import { PushEvent } from "@octokit/webhooks-types";
import { appConfig } from "../config.js";
import * as GraphQLUtil from "../lib/graphql-util.js";
import { GitHubOperationsContext } from "../types.js";

/**
 * Receives github webhook push events.
 * https://docs.github.com/en/webhooks-and-events/webhooks/webhook-events-and-payloads#push
 *
 * Features:
 * Checks if push event touched any files that Eave has subscriptions for;
 * any file subscriptions found will perform updates on connected documents.
 */
export default async function handler(
  event: PushEvent,
  context: GitHubOperationsContext,
) {
  const { ctx, octokit } = context;
  const event_name = "github_push_subscription_updates";
  ctx.feature_name = event_name;
  eaveLogger.debug("Processing push", ctx);
  const openaiClient = await OpenAIClient.getAuthedClient();

  // only handling branch push events for now; ignore tag pushes
  if (!event.ref.startsWith("refs/heads/")) {
    eaveLogger.debug(`Ignoring event with ref ${event.ref}`, ctx);
    return;
  }

  // fetch eave team id required for core_api requests
  const installationId = event.installation!.id;
  const teamResponse = await GetGithubInstallationOperation.perform({
    ctx,
    origin: appConfig.eaveOrigin,
    input: {
      github_integration: {
        github_install_id: `${installationId}`,
      },
    },
  });
  const eaveTeamId = teamResponse.team.id;

  // get file content so we can document the changes
  const query = await GraphQLUtil.loadQuery("getFileContents");

  // TODO: This event only contains a maximum of 20 commits. Additional commits need to be fetched from the API.
  // Also, this event is not triggered when more than 3 tags are pushed.
  // https://docs.github.com/webhooks-and-events/webhooks/webhook-events-and-payloads#push
  await Promise.all(
    event.commits.map(async (eventCommit) => {
      const modifiedFiles = Array.from(
        new Set([
          ...eventCommit.added,
          ...eventCommit.removed,
          ...eventCommit.modified,
        ]),
      );

      await Promise.all(
        modifiedFiles.map(async (eventCommitTouchedFilename) => {
          const branchName = event.ref.replace("refs/heads/", "");
          // b64 encode since our chosen ID delimiter '#' is a valid character in file paths and branch names
          const resourceId = Buffer.from(
            `${branchName}/${eventCommitTouchedFilename}`,
          ).toString("base64");
          // TODO: Move this eventId algorithm into a shared location
          const eventId = [event.repository.node_id, resourceId].join("#");

          // check if we are subscribed to this file
          let subscriptionResponse: GetSubscriptionResponseBody | null = null;
          try {
            subscriptionResponse = await GetSubscriptionOperation.perform({
              ctx,
              origin: appConfig.eaveOrigin,
              teamId: eaveTeamId,
              input: {
                subscription: {
                  source: {
                    platform: SubscriptionSourcePlatform.github,
                    event: SubscriptionSourceEvent.github_file_change,
                    id: eventId,
                  },
                },
              },
            });
          } catch (e: any) {
            // TODO: only catch 404?
            eaveLogger.error(e, ctx);
            return;
          }

          if (!subscriptionResponse || !subscriptionResponse.subscription) {
            return;
          }

          const variables: {
            repoOwner: Scalars["String"]["input"];
            repoName: Scalars["String"]["input"];
            commitOid: Scalars["String"]["input"];
            filePath: Scalars["String"]["input"];
          } = {
            repoOwner: event.repository.owner.name!,
            repoName: event.repository.name,
            commitOid: eventCommit.id,
            filePath: eventCommitTouchedFilename,
          };

          const fileContentsResponse = await octokit.graphql<{
            repository: Query["repository"];
          }>(query, variables);
          const fileContentsRepository = <Repository>(
            fileContentsResponse.repository!
          );
          const fileContentsCommit = <Commit>fileContentsRepository.object!;
          const fileContentsTreeEntry = <TreeEntry>fileContentsCommit.file!;
          const fileContentsBlob = <Blob>fileContentsTreeEntry.object!;
          const fileContents = fileContentsBlob.text!;

          // build a description of the file
          const codeDescription = [];

          const languageName = fileContentsTreeEntry.language?.name;
          if (languageName !== undefined) {
            codeDescription.push(`written in ${languageName}`);
          }

          const filePath = fileContentsTreeEntry.path;
          if (filePath !== undefined) {
            codeDescription.push(`in a file called "${filePath}"`);
          }

          const repositoryName = fileContentsRepository.name;
          codeDescription.push(
            `in a Github repository called "${repositoryName}"`,
          );

          const codeDescriptionString =
            codeDescription.length > 0
              ? `# The above code is ${codeDescription.join(", ")}`
              : "";

          // have AI explain the code change
          const summarizedContent = rollingSummary({
            client: openaiClient,
            content: fileContents,
            ctx,
          });

          // FIXME: Add this eslint exception to eslint config
          // eslint-disable-next-line operator-linebreak
          const prompt =
            `${summarizedContent}\n\n` +
            `${codeDescriptionString}. ` +
            "Explain what the above code does: ";

          // NOTE: According to the OpenAI docs, model gpt-3.5-turbo-0301 doesn't pay attention to the system messages,
          // but it seems it's specific to that model, and neither gpt-3.5-turbo or gpt-4 are affected, so watch out
          const openaiResponse = await openaiClient.createChatCompletion({
            parameters: {
              messages: [{ role: "user", content: prompt }],
              model: OpenAIModel.GPT4,
            },
            baseTimeoutSeconds: 120,
            documentId: subscriptionResponse.document_reference?.document_id,
            ctx,
          });

          const document: DocumentInput = {
            title: `Description of code in ${repositoryName} ${filePath}`,
            content: openaiResponse,
            parent: null,
          };

          await logEvent(
            {
              event_name,
              event_description:
                "updating a document subscribed to github file changes",
              event_source: "github webhook push event",
              opaque_params: {
                repoOwner: event.repository.owner.name,
                repoName: event.repository.name,
                filePath: eventCommitTouchedFilename,
                fileLanguage: languageName,
                document_id:
                  subscriptionResponse.document_reference?.document_id,
                eventId,
              },
              eave_team: teamResponse.team,
            },
            ctx,
          );

          await UpsertDocumentOperation.perform({
            ctx,
            origin: appConfig.eaveOrigin,
            teamId: eaveTeamId,
            input: {
              document,
              subscriptions: [subscriptionResponse.subscription],
            },
          });
        }),
      );
    }),
  );
}
