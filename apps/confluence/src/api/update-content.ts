import { Request, Response } from 'express';
import { AddOn } from 'atlassian-connect-express';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { UpdateContentRequestBody, UpdateContentResponseBody } from '@eave-fyi/eave-stdlib-ts/src/confluence-api/operations.js';
import * as openai from '@eave-fyi/eave-stdlib-ts/src/openai.js';
import { getAuthedConnectClient } from './util.js';
import { getPageById, updatePage } from '../confluence-client.js';

export default async function updateContent(req: Request, res: Response, addon: AddOn) {
  const client = await getAuthedConnectClient(req, addon);
  const { content } = <UpdateContentRequestBody>req.body;
  const page = await getPageById({ client, pageId: content.id });
  if (page === null) {
    eaveLogger.error(`Confluence page not found for ID ${content.id}`);
    res.status(500);
    return;
  }

  const existingBody = page.body?.storage?.value;
  if (existingBody === null) {
    eaveLogger.error(`Confluence page body is empty for ID ${content.id}`);
    res.status(500); // TODO: is 500 appropriate here?
    return;
  }

  const prompt = [
    'Merge the two HTML documents so that the unique information is retained, but duplicate information is removed.',
    'The resulting document should be should be formatted using plain HTML tags without any inline styling. The document will be embedded into another HTML document, so you should only include HTML tags needed for formatting, and omit tags such as <head>, <body>, <html>, and <!doctype>',
    'Maintain the overall document layout and style from the first document.',
    'Return only the merged document.\n',
    '=========================',
    'First Document:',
    '=========================',
    existingBody,
    '=========================',
    'Second Document:',
    '=========================',
    content.body,
    '=========================',
    'Merged Document:',
    '=========================',
  ].join('\n');

  // TODO: Token counting
  const openaiResponse = await openai.createChatCompletion({
    messages: [
      { role: 'user', content: prompt },
    ],
    model: openai.OpenAIModel.GPT4,
  });

  eaveLogger.debug({ message: 'OpenAI response', openaiResponse });

  const response = await updatePage({ client, page, body: openaiResponse });
  const responseBody: UpdateContentResponseBody = {
    content: response,
  };
  res.json(responseBody);
}
