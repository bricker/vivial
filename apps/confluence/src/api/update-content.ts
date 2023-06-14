import { Request, Response } from 'express';
import { AddOn } from 'atlassian-connect-express';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { UpdateContentRequestBody, UpdateContentResponseBody } from '@eave-fyi/eave-stdlib-ts/src/confluence-api/operations.js';
import OpenAIClient, * as openai from '@eave-fyi/eave-stdlib-ts/src/openai.js';
import { getEaveState } from '@eave-fyi/eave-stdlib-ts/src/lib/request-state.js';
import ConfluenceClient from '../confluence-client.js';

export default async function updateContent(req: Request, res: Response, addon: AddOn) {
  const eaveState = getEaveState(res);

  const confluenceClient = await ConfluenceClient.getAuthedConnectClient(req, addon);
  const { content } = <UpdateContentRequestBody>req.body;
  const page = await confluenceClient.getPageById({ pageId: content.id });
  if (page === null) {
    eaveLogger.error({ message: `Confluence page not found for ID ${content.id}`, eaveState });
    res.sendStatus(500);
    return;
  }

  const existingBody = page.body?.storage?.value;
  if (!existingBody) {
    eaveLogger.error({ message: `Confluence page body is empty for ID ${content.id}`, eaveState });
    res.sendStatus(500); // TODO: is 500 appropriate here?
    return;
  }

  const prompt = [
    'Merge the two HTML documents so that the unique information is retained, but duplicate information is removed.',
    'The resulting document should be should be formatted using plain HTML tags without any inline styling. The document will be embedded into another HTML document, so you should only include HTML tags needed for formatting, and omit tags such as <head>, <body>, <html>, and <!doctype>',
    'Maintain the overall document layout and style from the first document.',
    'Respond with only the merged document.',
    "If you can't perform this task because of insuffient information or any other reason, respond with the word \"UNABLE\" and nothing else.\n",
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
  const openaiClient = await OpenAIClient.getAuthedClient();
  const openaiResponse = await openaiClient.createChatCompletion({
    messages: [
      { role: 'user', content: prompt },
    ],
    model: openai.OpenAIModel.GPT4,
  }, eaveState);

  let newBody: string;

  if (openaiResponse.match(/UNABLE/i)) {
    eaveLogger.warning({ message: 'openai was unable to merge the documents. The new content will be used.', eaveState });
    newBody = content.body;
  } else {
    newBody = openaiResponse;
  }

  const response = await confluenceClient.updatePage({ page, body: newBody });
  const responseBody: UpdateContentResponseBody = {
    content: response,
  };
  res.json(responseBody);
}
