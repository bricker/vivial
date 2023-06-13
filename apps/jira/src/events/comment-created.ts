import { Request, Response } from 'express';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import OpenAIClient, { OpenAIModel } from '@eave-fyi/eave-stdlib-ts/src/openai.js';
import { AddOn } from 'atlassian-connect-express';
import { IncomingMessage } from 'http';
import { queryConnectInstallation } from '@eave-fyi/eave-stdlib-ts/src/core-api/operations/connect.js';
import { AtlassianProduct } from '@eave-fyi/eave-stdlib-ts/src/core-api/models/connect.js';
import appConfig from '../config.js';
import { CommentCreatedEventPayload, ContentType, User } from '../types.js';

export default async function commentCreatedEventHandler({ req, res, addon }: { req: Request, res: Response, addon: AddOn }) {
  // FIXME: Redact auth header
  eaveLogger.debug('received webhook event', { body: req.body, headers: req.headers });
  const openaiClient = await OpenAIClient.getAuthedClient();
  const payload = <CommentCreatedEventPayload>req.body;
  const client = addon.httpClient(req);

  if (payload.comment.author.accountType === 'app') {
    eaveLogger.info('Ignoring app comment');
    return;
  }

  // [~accountid:712020:d50089b8-586c-4f54-a3ad-db70381e4cae]
  const mentionAccountIds = payload.comment.body.match(/\[~accountid:(.+?)\]/i);
  if (!mentionAccountIds) {
    eaveLogger.info('No mentions in this message, ignoring');
    return;
  }

  // We have to use an old-fashioned Promise chain this way because the atlassian express library
  // uses the request library directly and uses the callback function interface.
  const eaveMentioned = await Promise.any(mentionAccountIds.map((accountId) => {
    return new Promise<boolean>((resolve, reject) => {
      client.get({
        url: '/rest/api/3/user',
        qs: { accountId },
      }, (err: any, response: IncomingMessage, body: string) => {
        if (err) {
          reject();
          return;
        }
        if (response.statusCode === 200) {
          const user = <User>JSON.parse(body);
          if (user.accountType === 'app' && user.displayName === 'Eave for Jira') {
            resolve(true);
          } else {
            reject();
          }
        }
      }).catch(reject);
    });
  }));

  if (!eaveMentioned) {
    eaveLogger.info('Eave not mentioned, ignoring');
    return;
  }

  const prompt = [
    'Is the following message asking you to look up some existing documentation? Say either Yes or No.',
    'Message:',
    '###',
    payload.comment.body,
    '###',
  ].join('\n');

  const openaiResponse = await openaiClient.createChatCompletion({
    messages: [
      { role: 'user', content: prompt },
    ],
    model: OpenAIModel.GPT4,
  });

  eaveLogger.debug('OpenAI response', { openaiResponse });

  if (!openaiResponse.match(/yes/i)) {
    eaveLogger.debug('Comment ignored');
    return;
  }

  const connectInstallation = await queryConnectInstallation({
    origin: appConfig.eaveOrigin,
    input: {
      connect_integration: {
        product: AtlassianProduct.jira,
        client_key: client.clientKey,
      },
    },
  });

  const teamId = connectInstallation.team?.id;
  if (!teamId) {
    eaveLogger.warn({ message: 'No teamId available', clientKey: client.clientKey });
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
    await client.post({
      url: `/rest/api/3/issue/${payload.issue.id}/comment`,
      json: true,
      body: {
        body: {
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
        },
      },
    });
  }
}
