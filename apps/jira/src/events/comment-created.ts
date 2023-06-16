import { Request, Response } from 'express';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import OpenAIClient, { OpenAIModel } from '@eave-fyi/eave-stdlib-ts/src/openai.js';
import { queryConnectInstallation } from '@eave-fyi/eave-stdlib-ts/src/core-api/operations/connect.js';
import { SearchDocumentsResponseBody, searchDocuments } from '@eave-fyi/eave-stdlib-ts/src/core-api/operations/documents.js';
import { AtlassianProduct } from '@eave-fyi/eave-stdlib-ts/src/core-api/models/connect.js';
import { EaveRequestState, getEaveState } from '@eave-fyi/eave-stdlib-ts/src/lib/request-state.js';
import { ADFLinkMark, ADFMentionNode, ADFNode, ADFRootNode, ADFTextNode, ADFBlockNodeType, ADFInlineNodeType, ADFParagraphNode, ADFMarkType, ADFListItemNode, ADFChildBlockNodeType, ADFBulletListNode } from '@eave-fyi/eave-stdlib-ts/src/connect/types/adf.js';
import appConfig from '../config.js';
import JiraClient from '../jira-client.js';
import { JiraCommentCreatedEventPayload } from '../types.js';

const ACCOUNT_ID_RE = /\[~accountid:(.+?)\]/ig;

enum MessageIntent {
  search = 'search',
}

export default async function commentCreatedEventHandler({ req, res, jiraClient }: { req: Request, res: Response, jiraClient: JiraClient }) {
  const eaveState = getEaveState(res);
  eaveLogger.debug({ message: 'received comment created webhook event', eaveState });
  const openaiClient = await OpenAIClient.getAuthedClient();
  const payload = <JiraCommentCreatedEventPayload>req.body;

  if (!payload.issue) {
    eaveLogger.warn({ message: 'Missing payload.issue' });
    res.sendStatus(400);
    return;
  }

  if (payload.comment.author.accountType === 'app') {
    eaveLogger.info({ message: 'Ignoring app comment', eaveState });
    res.sendStatus(200);
    return;
  }

  // [~accountid:712020:d50089b8-586c-4f54-a3ad-db70381e4cae]
  const mentionAccountIds = Array.from(payload.comment.body.matchAll(ACCOUNT_ID_RE));

  const eaveMentioned = await Promise.any(mentionAccountIds.map(async (match) => {
    const user = await jiraClient.getUser({ accountId: match[1]! });
    if (user?.accountType === 'app' && user?.displayName === 'Eave for Jira') {
      return true;
    }
    return false;
  }));

  if (!eaveMentioned) {
    eaveLogger.info({ message: 'Eave not mentioned, ignoring', eaveState });
    res.sendStatus(200);
    return;
  }

  // TODO: Get this from cache
  const connectInstallation = await queryConnectInstallation({
    origin: appConfig.eaveOrigin,
    input: {
      connect_integration: {
        product: AtlassianProduct.jira,
        client_key: jiraClient.client.clientKey,
      },
    },
  });

  const teamId = connectInstallation.team?.id;
  if (!teamId) {
    eaveLogger.warn({ message: 'No teamId available', clientKey: jiraClient.client.clientKey, eaveState });
    res.sendStatus(400);
    return;
  }

  const cleanedBody = cleanCommentBody(payload.comment.body);
  const intent = await getIntent({ comment: cleanedBody, openaiClient, eaveState });

  if (intent !== MessageIntent.search) {
    // No handling for this scenario yet.
    eaveLogger.warn({ message: 'Unknown intent', eaveState });
    eaveLogger.debug({ message: 'comment body', cleanedBody });
    res.sendStatus(200);
    return;
  }

  const searchQuery = await getSearchQuery({ comment: cleanedBody, openaiClient, eaveState });

  const searchResults = await searchDocuments({
    origin: appConfig.eaveOrigin,
    teamId,
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
  return comment.replace(ACCOUNT_ID_RE, '');
}

async function getSearchQuery({ comment, openaiClient, eaveState }: { comment: string, openaiClient: OpenAIClient, eaveState: EaveRequestState }): Promise<string> {
  const prompt = [
    'Extract a key term or phrase from this message that can be used as a full-text search query to find relevant documentation.',
    'Do not include any quotes or other punctuation.',
    'Message:',
    '###',
    comment,
    '###',
  ].join('\n');

  const response = await openaiClient.createChatCompletion({
    messages: [
      { role: 'user', content: prompt },
    ],
    model: OpenAIModel.GPT_35_TURBO_16K,
  }, eaveState);

  return response;
}

async function getIntent({ comment, openaiClient, eaveState }: { comment: string, openaiClient: OpenAIClient, eaveState: EaveRequestState }): Promise<MessageIntent | null> {
  const prompt = [
    'Is the following message asking you to look up some existing documentation? Say either Yes or No.',
    'Message:',
    '###',
    comment,
    '###',
  ].join('\n');

  const response = await openaiClient.createChatCompletion({
    messages: [
      { role: 'user', content: prompt },
    ],
    model: OpenAIModel.GPT_35_TURBO_16K,
  }, eaveState);

  if (response.match(/yes/i)) {
    return MessageIntent.search;
  } else {
    return null;
  }
}

function buildEaveResponse({ searchResults, payload }: { searchResults: SearchDocumentsResponseBody, payload: JiraCommentCreatedEventPayload }): ADFRootNode {
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
            text: ' I found some relevant documentation:',
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
