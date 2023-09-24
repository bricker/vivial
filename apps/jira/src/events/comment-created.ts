import { logEvent } from "@eave-fyi/eave-stdlib-ts/src/analytics.js";
import { ADFBlockNodeType, ADFBulletListNode, ADFChildBlockNodeType, ADFInlineNodeType, ADFLinkMark, ADFListItemNode, ADFMarkType, ADFMentionNode, ADFNode, ADFParagraphNode, ADFRootNode, ADFTextNode } from "@eave-fyi/eave-stdlib-ts/src/connect/types/adf.js";
import { AtlassianProduct } from "@eave-fyi/eave-stdlib-ts/src/core-api/models/connect.js";
import { QueryConnectInstallationOperation } from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/connect.js";
import { SearchDocumentsOperation, SearchDocumentsResponseBody } from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/documents.js";
import { LogContext, eaveLogger } from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import { OpenAIModel } from "@eave-fyi/eave-stdlib-ts/src/transformer-ai/models.js";
import OpenAIClient from "@eave-fyi/eave-stdlib-ts/src/transformer-ai/openai.js";
import { Request, Response } from "express";
import appConfig from "../config.js";
import JiraClient from "../jira-client.js";
import { JiraCommentCreatedEventPayload, JiraUser } from "../types.js";

const ACCOUNT_ID_RE = /\[~accountid:(.+?)\]/gi;

enum MessageIntent {
  search = "search",
}

export default async function commentCreatedEventHandler({ req, res, jiraClient }: { req: Request; res: Response; jiraClient: JiraClient }) {
  const ctx = LogContext.load(res);

  eaveLogger.debug("received comment created webhook event", ctx);
  const openaiClient = await OpenAIClient.getAuthedClient();
  const payload = <JiraCommentCreatedEventPayload>req.body;

  if (!payload.issue) {
    eaveLogger.warning("Missing payload.issue", ctx);
    res.sendStatus(400);
    return;
  }

  if (payload.comment.author.accountType === "app") {
    eaveLogger.info("Ignoring app comment", ctx);
    res.sendStatus(200);
    return;
  }

  // [~accountid:712020:d50089b8-586c-4f54-a3ad-db70381e4cae]
  const mentionAccountIds = Array.from(payload.comment.body.matchAll(ACCOUNT_ID_RE));

  const eaveMentioned = await Promise.any(
    mentionAccountIds.map(async (match) => {
      const user = await jiraClient.getUser({ accountId: match[1]! });
      if (isEave(user)) {
        return true;
      }
      return false;
    }),
  );

  if (!eaveMentioned) {
    eaveLogger.info("Eave not mentioned, ignoring", ctx);
    res.sendStatus(200);
    return;
  }

  // TODO: Get this from cache
  const connectInstallation = await QueryConnectInstallationOperation.perform({
    ctx,
    origin: appConfig.eaveOrigin,
    input: {
      connect_integration: {
        product: AtlassianProduct.jira,
        client_key: jiraClient.client.clientKey,
      },
    },
  });

  const team = connectInstallation.team;
  if (!team) {
    eaveLogger.warning("No teamId available", { clientKey: jiraClient.client.clientKey }, ctx);
    res.sendStatus(400);
    return;
  }

  try {
    await logEvent(
      {
        event_description: "Eave was mentioned in a Jira comment",
        event_name: "eave_mentioned",
        event_source: "jira comment-created event handler",
        eave_team: JSON.stringify(team),
        opaque_params: JSON.stringify({
          message: payload.comment.body,
        }),
      },
      ctx,
    );
  } catch (e: any) {
    eaveLogger.error(e, ctx);
  }

  const cleanedBody = cleanCommentBody(payload.comment.body);
  const intent = await getIntent({ comment: cleanedBody, openaiClient, ctx });

  if (intent !== MessageIntent.search) {
    // No handling for this scenario yet.
    eaveLogger.warning("Unknown intent", ctx);
    eaveLogger.debug("comment body", { cleanedBody }, ctx);
    res.sendStatus(200);
    return;
  }
  ctx.feature_name = "jira_document_search";

  const searchQuery = await getSearchQuery({ comment: cleanedBody, openaiClient, ctx });

  const searchResults = await SearchDocumentsOperation.perform({
    ctx,
    origin: appConfig.eaveOrigin,
    teamId: team.id,
    input: {
      query: searchQuery,
    },
  });

  const commentDoc = buildEaveResponse({ searchResults, payload });
  await jiraClient.postComment({ issueId: payload.issue.id, commentBody: commentDoc });
  res.sendStatus(200);
}

function cleanCommentBody(comment: string): string {
  // FIXME: all this does is remove user mentions, but we should instead replace them with a real name.
  return comment.replace(ACCOUNT_ID_RE, "");
}

async function getSearchQuery({ comment, openaiClient, ctx }: { comment: string; openaiClient: OpenAIClient; ctx: LogContext }): Promise<string> {
  const prompt = ["Extract a key term (1-3 words) from this message that can be used as a full-text search query to find relevant documentation. Do not include any quotes or other punctuation in your response.", "Examples:", "###", "Message: Is there any documentation about jelly beans?", "Response: jelly beans", "Message: do you have information about the space station or space ships?", "Response: space ships", "###", "Message:", "###", comment, "###"].join("\n");

  const response = await openaiClient.createChatCompletion({
    parameters: {
      messages: [{ role: "user", content: prompt }],
      model: OpenAIModel.GPT4,
    },
    ctx,
  });

  return response;
}

async function getIntent({ comment, openaiClient, ctx }: { comment: string; openaiClient: OpenAIClient; ctx: LogContext }): Promise<MessageIntent | null> {
  const prompt = ["Is the following message asking you to find some existing documentation, recall some information you may have, or look something up? Say either Yes or No.", "Message:", "###", comment, "###"].join("\n");

  const response = await openaiClient.createChatCompletion({
    parameters: {
      messages: [{ role: "user", content: prompt }],
      model: OpenAIModel.GPT4,
    },
    ctx,
  });

  if (response.match(/yes/i)) {
    return MessageIntent.search;
  } else {
    return null;
  }
}

function buildEaveResponse({ searchResults, payload }: { searchResults: SearchDocumentsResponseBody; payload: JiraCommentCreatedEventPayload }): ADFRootNode {
  let content: ADFNode[];

  const mentionNode: ADFMentionNode = {
    type: ADFInlineNodeType.mention,
    attrs: {
      id: payload.comment.author.accountId,
    },
  };

  if (searchResults.documents.length > 0) {
    const listItemNodes = searchResults.documents.map((document): ADFListItemNode => {
      return <ADFListItemNode>{
        type: ADFChildBlockNodeType.listItem,
        content: [
          <ADFParagraphNode>{
            type: ADFBlockNodeType.paragraph,
            content: [
              <ADFTextNode>{
                type: ADFInlineNodeType.text,
                text: document.title,
                marks: [
                  <ADFLinkMark>{
                    type: ADFMarkType.link,
                    attrs: {
                      href: document.url,
                      title: document.title,
                    },
                  },
                ],
              },
            ],
          },
        ],
      };
    });

    content = [
      <ADFParagraphNode>{
        type: ADFBlockNodeType.paragraph,
        content: [
          mentionNode,
          <ADFTextNode>{
            type: ADFInlineNodeType.text,
            // The leading space is to leave room after the mention
            text: " I found some relevant documentation:",
          },
        ],
      },
      <ADFBulletListNode>{
        type: ADFBlockNodeType.bulletList,
        content: listItemNodes,
      },
    ];
  } else {
    content = [
      <ADFParagraphNode>{
        type: ADFBlockNodeType.paragraph,
        content: [
          mentionNode,
          <ADFTextNode>{
            type: ADFInlineNodeType.text,
            // The leading space is to leave room after the mention
            text: " I couldn't find any relevant documentation",
          },
        ],
      },
    ];
  }

  const commentDoc: ADFRootNode = {
    type: ADFBlockNodeType.doc,
    version: 1,
    content,
  };

  return commentDoc;
}

function isEave(user?: JiraUser) {
  return user && user.accountId === appConfig.eaveJiraAppAccountId;
}
