import { eaveLogger } from "./logging.js";
import {
  assertValidSyntax,
  parseFunctionsAndComments,
  writeUpdatedCommentsIntoFileString,
} from "./parsing/function-parsing.js";
import { getProgrammingLanguageByFilePathOrName } from "./programming-langs/language-mapping.js";
import { CtxArg } from "./requests.js";
import { OpenAIModel } from "./transformer-ai/models.js";
import OpenAIClient, { formatprompt } from "./transformer-ai/openai.js";
import * as AIUtil from "./transformer-ai/util.js";

/**
 * This function updates the documentation of a given file. It first identifies the programming language of the file based on its extension.
 * If the language is not supported, it logs an error and returns null. Otherwise, it parses the functions and comments from the file.
 * If no data can be parsed, it logs an error and returns null. For each parsed function, it generates a summary and uses it to create or update the documentation.
 * If the function already has documentation, the function merges the old and new documentation, preferring the new one in case of conflicts.
 * Finally, it writes the updated comments back into the file content.
 *
 * @param {Object} params - The parameters for the function.
 * @param {string} params.currContent - The current content of the file.
 * @param {string} params.filePath - The path of the file.
 * @param {OpenAIClient} params.openaiClient - The OpenAI client to use for generating documentation.
 * @param {Object} params.ctx - The context for logging.
 * @param {string} params.fileNodeId - The GitHub graphql node ID of the file. See https://docs.github.com/en/graphql/reference/interfaces#node for more details.
 * @param {OpenAIModel} [params.model=OpenAIModel.GPT4] - The OpenAI model to use for generating documentation.
 * @returns {Promise<string|null>} The updated file content, or null if the language is not supported, no data could be parsed, or if unable to create updated document.
 */
export async function updateDocumentation({
  currContent,
  filePath,
  openaiClient,
  ctx,
  fileNodeId,
  model = OpenAIModel.GPT4,
}: CtxArg & {
  currContent: string;
  filePath: string;
  openaiClient: OpenAIClient;
  fileNodeId: string;
  model?: OpenAIModel;
}): Promise<string | null> {
  // load language from file extension map file
  const flang = getProgrammingLanguageByFilePathOrName(filePath);
  if (!flang) {
    // file extension not found in the map file, which makes it impossible for us to
    // put docs in a syntactially valid comment; exit early
    eaveLogger.error(
      `No matching language found for file path: "${filePath}"`,
      ctx,
    );
    return null;
  }

  const parsedData = parseFunctionsAndComments({
    content: currContent,
    filePath,
    language: flang,
    ctx,
  });
  if (parsedData.length === 0) {
    eaveLogger.error(`Unable to parse ${flang} from file ${filePath}`, ctx);
    return null;
  }

  // update parsedData objects in place w/ updatedCommentStrings
  await Promise.all(
    parsedData.map(async (funcData) => {
      // convert long function strings to a summary for docs writing to prevent AI from getting overwhelmed by
      // implementation details in raw code file (and to account for functions longer than model context)
      const summarizedFunction = await AIUtil.rollingSummary({
        client: openaiClient,
        content: funcData.func,
        ctx,
      });

      // update docs, or write new ones if currDocs is empty/undefined
      // TODO: experiment performance quality on dif types of comments:
      //      (1. update own comment 2. write from scratch 3. update existing detailed docs 4. fix slightly incorrect docs)
      const docsPrompt = formatprompt(
        `Write a ${flang} doc comment for the following function.`,
        `Be succinct, excluding redundant or unnecessary terms like "This function {...}".`,
        "Do not include surrounding markdown-style backticks.\n",
        "===",
        summarizedFunction,
        "===",
      );
      const newDocsResponse = await openaiClient.createChatCompletion({
        parameters: {
          messages: [
            {
              role: "system",
              content: `You must respond with only a valid ${flang} doc comment.`,
            },
            {
              role: "user",
              content: docsPrompt,
            },
          ],
          model,
          temperature: 0,
        },
        documentId: fileNodeId,
        ctx,
      });

      // if there were already existing docs, update them using newly written docs
      let updatedDocs = newDocsResponse;
      if (funcData.comment) {
        updatedDocs = await openaiClient.createChatCompletion({
          parameters: {
            messages: [
              {
                role: "system",
                content: `You must respond with only a valid ${flang} doc comment.`,
              },
              {
                role: "user",
                content: formatprompt(
                  `Merge these two ${flang} doc comments, maintaining the important information.`,
                  `If there are any conflicts of content, prefer the new documentation. Return only the ${flang} doc comment.\n`,
                  "Old documentation:",
                  "===",
                  funcData.comment,
                  "===\n",
                  "New documentation:",
                  "===",
                  newDocsResponse,
                  "===",
                ),
              },
            ],
            model,
            temperature: 0,
          },
          documentId: fileNodeId,
          ctx,
        });
      }

      // clean updated docs; make sure we dont write white space that could be lint errors
      updatedDocs = updatedDocs
        .split("\n")
        .map((line) => line.trimEnd())
        .join("\n");

      funcData.updatedComment = updatedDocs;
    }),
  );

  // write `updatedComment` data back into currContent string
  const updatedContent = writeUpdatedCommentsIntoFileString(
    currContent,
    parsedData,
  );

  // assert syntax check; never write syntax errors to customer code!
  try {
    assertValidSyntax({ content: updatedContent, filePath });
  } catch {
    eaveLogger.error("Eave wrote syntactically incorrect code", ctx);
    // return existing file content with no changes
    return currContent;
  }

  return updatedContent;
}
