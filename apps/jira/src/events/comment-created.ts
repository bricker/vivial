import { Request, Response } from 'express';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import OpenAIClient, { OpenAIModel } from '@eave-fyi/eave-stdlib-ts/src/openai.js';
import { AddOn } from 'atlassian-connect-express';
import { IncomingMessage } from 'http';
import { queryConnectInstallation } from '@eave-fyi/eave-stdlib-ts/src/core-api/operations/connect.js';
import { searchDocuments } from '@eave-fyi/eave-stdlib-ts/src/core-api/operations/documents.js';
import { AtlassianProduct } from '@eave-fyi/eave-stdlib-ts/src/core-api/models/connect.js';
import { getEaveState } from '@eave-fyi/eave-stdlib-ts/src/lib/request-state.js';
import appConfig from '../config.js';
import { AtlassianDoc, CommentCreatedEventPayload, Content, ContentType, User } from '../types.js';
import JiraClient from '../jira-client.js';

export default async function commentCreatedEventHandler({ req, res, jiraClient }: { req: Request, res: Response, jiraClient: JiraClient }) {
  const eaveState = getEaveState(res);
  // FIXME: Redact auth header
  eaveLogger.debug({ message: 'received comment created webhook event', eaveState });
  const openaiClient = await OpenAIClient.getAuthedClient();
  const payload = <CommentCreatedEventPayload>req.body;

  if (payload.comment.author.accountType === 'app') {
    eaveLogger.info({ message: 'Ignoring app comment', eaveState });
    return;
  }

  // [~accountid:712020:d50089b8-586c-4f54-a3ad-db70381e4cae]
  const mentionAccountIds = Array.from(payload.comment.body.matchAll(/\[~accountid:(.+?)\]/ig));

  // We have to use an old-fashioned Promise chain this way because the atlassian express library
  // uses the request library directly and uses the callback function interface.
  const eaveMentioned = await Promise.any(mentionAccountIds.map(async (match) => {
    const user = await jiraClient.getUser({ accountId: match[1]! });
    if (user?.accountType === 'app' && user?.displayName === 'Eave for Jira') {
      return true;
    }
    return false;
  }));

  if (!eaveMentioned) {
    eaveLogger.info({ message: 'Eave not mentioned, ignoring', eaveState });
    return;
  }

  const prompt = [
    'Is the following message asking you to look up some existing documentation? Say either Yes or No.',
    'Message:',
    '###',
    payload.comment.body,
    '###',
  ].join('\n');

  eaveLogger.debug({ message: 'openai prompt', prompt, eaveState });
  const openaiResponse = await openaiClient.createChatCompletion({
    messages: [
      { role: 'user', content: prompt },
    ],
    model: OpenAIModel.GPT4,
  }, eaveState);

  eaveLogger.debug({ message: 'openai response', prompt, openaiResponse, eaveState });

  if (!openaiResponse.match(/yes/i)) {
    eaveLogger.debug({ message: 'Comment ignored', eaveState });
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
    eaveLogger.warning({ message: 'No teamId available', clientKey: jiraClient.client.clientKey, eaveState });
    return;
  }

  const searchResults = await searchDocuments({
    origin: appConfig.eaveOrigin,
    teamId,
    input: {
      query: payload.comment.body,
    },
  });

  if (payload.issue !== undefined) {
    const commentBody: AtlassianDoc = {
      type: ContentType.doc,
      version: 1,
      content: [
        {
          type: 'paragraph',
          content: searchResults.documents.map((document) => (
            {
              type: ContentType.text,
              text: document.title,
              marks: [
                {
                  type: ContentType.link,
                  attrs: {
                    href: document.url,
                    title: document.title,
                  },
                },
              ],
            }
          )),
        },
      ],
    };

    await jiraClient.postComment({ issueId: payload.issue.id, commentBody });
  }
}
