import eaveLogger, { LogContext } from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { UpdateContentRequestBody, UpdateContentResponseBody } from '@eave-fyi/eave-stdlib-ts/src/confluence-api/operations.js';
import OpenAIClient, * as openai from '@eave-fyi/eave-stdlib-ts/src/openai.js';
import { ExpressHandlerArgs } from '@eave-fyi/eave-stdlib-ts/src/requests.js';
import { ConfluenceClientArg } from './util.js';

export default async function updateContent({ req, res, confluenceClient }: ExpressHandlerArgs & ConfluenceClientArg) {
  const ctx = LogContext.load(res);
  const { content } = <UpdateContentRequestBody>req.body;
  const page = await confluenceClient.getPageById({ pageId: content.id });
  if (page === null) {
    eaveLogger.error(`Confluence page not found for ID ${content.id}`, ctx);
    res.sendStatus(500);
    return;
  }

  // const existingBody = page.body?.storage?.value;
  // if (!existingBody) {
  //   eaveLogger.error(`Confluence page body is empty for ID ${content.id}`, ctx);
  //   res.sendStatus(500); // TODO: is 500 appropriate here?
  //   return;
  // }

  // const prompt = [
  //   'Merge the two HTML documents so that the unique information is retained, but duplicate information is removed.',
  //   'The resulting document should be should be formatted using plain HTML tags without any inline styling. The document will be embedded into another HTML document, so you should only include HTML tags needed for formatting, and omit tags such as <head>, <body>, <html>, and <!doctype>',
  //   'Maintain the overall document layout and style from the first document.',
  //   'Respond with only the merged document.',
  //   "If you can't perform this task because of insuffient information or any other reason, respond with the word \"UNABLE\" and nothing else.\n",
  //   '=========================',
  //   'First Document:',
  //   '=========================',
  //   existingBody,
  //   '=========================',
  //   'Second Document:',
  //   '=========================',
  //   content.body,
  //   '=========================',
  //   'Merged Document:',
  //   '=========================',
  // ].join('\n');

  // // TODO: Token counting
  // const openaiClient = await OpenAIClient.getAuthedClient();
  // const openaiResponse = await openaiClient.createChatCompletion({
  //   messages: [
  //     { role: 'user', content: prompt },
  //   ],
  //   model: openai.OpenAIModel.GPT4,
  // }, ctx);

  // let newBody: string;

  // if (openaiResponse.match(/UNABLE/i)) {
  //   eaveLogger.warning('openai was unable to merge the documents. The new content will be used.', ctx);
  //   newBody = content.body;
  // } else {
  //   newBody = openaiResponse;
  // }

  const response = await confluenceClient.updatePage({ page, body: content.body });
  const responseBody: UpdateContentResponseBody = {
    content: response,
  };
  res.json(responseBody);
}
