import path from 'path';
import { writeUpdatedCommentsIntoFileString, parseFunctionsAndComments } from './parsing/function-parsing.js';
import eaveLogger, { LogContext } from './logging.js';
import * as AIUtil from './transformer-ai/util.js';
import { getExtensionMap } from './language-mapping.js';
import OpenAIClient, { formatprompt } from './transformer-ai/openai.js';
import { OpenAIModel } from './transformer-ai/models.js';

/**
 * Given the current content of a file, returns the same file
 * content but with the documentation updated to reflect any code changes.
 *
 * @param currContent a file's content in plaintext
 * @param filePath file path correlated with `currContent` file content
 * @param openaiClient
 * @param ctx extra context for more detailed logs
 * @param model the AI model to use to generate new documentation (Default: OpenAIModel.GPT4)
 * @returns the same code content as `currContent` but with doc strings updated, or null if unable to create updated document
 */
export async function updateDocumentation(
  currContent: string,
  filePath: string,
  openaiClient: OpenAIClient,
  ctx: LogContext,
  model: OpenAIModel = OpenAIModel.GPT4,
): Promise<string | null> {
  // load language from file extension map file
  const extName = `${path.extname(filePath).toLowerCase()}`;
  const flang = (await getExtensionMap())[extName];
  if (!flang) {
    // file extension not found in the map file, which makes it impossible for us to
    // put docs in a syntactially valid comment; exit early
    eaveLogger.error(`No matching language found for file extension: "${extName}"`);
    return null;
  }

  const parsedData = parseFunctionsAndComments(currContent, extName, flang);
  if (parsedData.length === 0) {
    eaveLogger.error(`Unable to parse ${flang} from ${extName} file`);
    return null;
  }

  // update parsedData objects in place w/ updatedCommentStrings
  await Promise.all(parsedData.map(async (funcData) => {
    // convert long function strings to a summary for docs writing to prevent AI from getting overwhelmed by
    // implementation details in raw code file (and to account for functions longer than model context)
    const summarizedFunction = await AIUtil.rollingSummary(openaiClient, funcData.func);

    // update docs, or write new ones if currDocs is empty/undefined
    // TODO: retest w/ summarized function
    // TODO: experiment performance qulaity on dif types of comments:
    //      (1. update own comment 2. write from scratch 3. update existing detailed docs 4. fix slightly incorrect docs)
    const docsPrompt = formatprompt(
      `Write a ${flang} doc comment for the following function.\n`,
      '===',
      summarizedFunction,
      '===',
    );
    const newDocsResponse = await openaiClient.createChatCompletion({
      parameters: {
        messages: [
          {
            role: 'system',
            content: `You must respond with only a valid ${flang} doc comment.`,
          },
          {
            role: 'user',
            content: docsPrompt,
          },
        ],
        model,
        temperature: 0,
      },
      ctx,
    });

    // if there were already existing docs, update them using newly written docs
    // TODO: how to handle comment merging...
    let updatedDocs = newDocsResponse;
    if (funcData.comment) {
      updatedDocs = await openaiClient.createChatCompletion({
        parameters: {
          messages: [
            {
              role: 'system',
              content: `You must respond with only a valid ${flang} doc comment.`,
            },
            {
              role: 'user',
              content: formatprompt(
                `Merge these two ${flang} doc comments, maintaining the important information.`,
                `If there are any conflicts of content, prefer the new documentation. Return only the ${flang} doc comment.\n`,
                'Old documentation:',
                '===',
                funcData.comment,
                '===\n',
                'New documentation:',
                '===',
                newDocsResponse,
                '===',
              ),
            },
          ],
          model,
          temperature: 0,
        },
        ctx,
      });
    }

    funcData.updatedComment = updatedDocs;
  }));

  // write `updatedComment` data back into currContent string
  return writeUpdatedCommentsIntoFileString(currContent, parsedData);
}
