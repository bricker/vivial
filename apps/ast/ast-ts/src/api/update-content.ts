import eaveLogger, { LogContext } from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { UpdateContentRequestBody, UpdateContentResponseBody } from '@eave-fyi/eave-stdlib-ts/src/confluence-api/operations.js';
import { ExpressHandlerArgs } from '@eave-fyi/eave-stdlib-ts/src/requests.js';
import OpenAIClient, { OpenAIModel } from '@eave-fyi/eave-stdlib-ts/src/openai.js';
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

  const existingBody = page.body?.storage?.value;
  let newBody = content.body;

  if (existingBody) {
    const prompt = [
      'Merge the following two HTML documents so that the unique information is retained, but duplicate information is removed.',
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

    // Check which model to use based on token count.
    // The idea with dividing by 1.5 is that the prompt contains roughly 2/3 of the full token usage,
    // because the prompt + response contains three total documents.
    let model: OpenAIModel | undefined;
    if (OpenAIClient.tokenCount(prompt, OpenAIModel.GPT4) < OpenAIClient.maxTokens(OpenAIModel.GPT4) / 1.5) {
      model = OpenAIModel.GPT4;
    } else if (OpenAIClient.tokenCount(prompt, OpenAIModel.GPT_35_TURBO_16K) < OpenAIClient.maxTokens(OpenAIModel.GPT_35_TURBO_16K) / 1.5) {
      model = OpenAIModel.GPT_35_TURBO_16K;
    }

    if (model) {
      const openaiClient = await OpenAIClient.getAuthedClient();
      const openaiResponse = await openaiClient.createChatCompletion({
        parameters: {
          messages: [
            { role: 'user', content: prompt },
          ],
          model: OpenAIModel.GPT4,
        },
        baseTimeoutSeconds: 120,
        ctx,
      });

      if (openaiResponse.match(/UNABLE/i)) {
        eaveLogger.warning('openai was unable to merge the documents. The new content will be used.', ctx);
      } else {
        newBody = openaiResponse;
      }
    } else {
      eaveLogger.warning('Prompt is too big for OpenAI. Document will be overwritten', ctx);
    }
  }

  const response = await confluenceClient.updatePage({ page, body: newBody });
  const responseBody: UpdateContentResponseBody = {
    content: response,
  };
  res.json(responseBody);
}
