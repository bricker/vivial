import {
  ChatCompletionRequestMessageRoleEnum,
  Configuration,
  CreateChatCompletionRequest,
  CreateChatCompletionResponse,
  OpenAIApi,
} from "openai";
import { v4 as uuidv4 } from "uuid";
import { logGptRequest } from "../analytics.js";
import { sharedConfig } from "../config.js";
import { LogContext, eaveLogger } from "../logging.js";
import { CtxArg } from "../requests.js";
import { redact } from "../util.js";
import { modelFromString } from "./models.js";
import * as costCounter from "./token-counter.js";

// eslint-disable-next-line operator-linebreak
export const PROMPT_PREFIX =
  "You are Eave, a documentation expert. " +
  "Your job is to write, find, and organize robust, detailed documentation of this organization's information, decisions, projects, and procedures. " +
  "You are responsible for the quality and integrity of this organization's documentation.";

/**
 * Formats a series of prompts by removing common leading whitespace from each line of each prompt.
 * If a prompt is a single line or has no common leading whitespace, it is left unchanged.
 * The formatted prompts are then joined together with a newline character between each.
 *
 * @param prompts - An array of strings, each representing a prompt to be formatted.
 * @returns A single string containing all the formatted prompts, separated by newline characters.
 */
export function formatprompt(...prompts: string[]): string {
  const prompt: string[] = [];
  for (const s of prompts) {
    let chunks = s.split("\n");
    if (chunks.length <= 1) {
      // not a multiline string; nothing to dedent
      prompt.push(s);
      continue;
    }

    const commonLeadingWhitespaceLength = chunks.reduce((len, line) => {
      // Ignore empty lines
      if (line.trim() === "") {
        return len;
      }

      const m = line.match(/^\s*/);
      // 'm' will never be null, because every string will match the regex. This check is for the typechecker.
      if (m && m[0].length < len) {
        len = m[0].length;
      }
      return len;
    }, Infinity);

    if (commonLeadingWhitespaceLength === Infinity) {
      prompt.push(s);
      continue;
    }

    chunks = chunks.map((line) => line.slice(commonLeadingWhitespaceLength));
    prompt.push(chunks.join("\n"));
  }
  return prompt.join("\n");
}

export default class OpenAIClient {
  client: OpenAIApi;

  /**
   * Retrieves an authenticated OpenAI client.
   *
   * This method asynchronously fetches the OpenAI API key and organization from the shared configuration,
   * creates a new configuration object with these values, and then initializes a new OpenAI client with this configuration.
   *
   * @returns {Promise<OpenAIClient>} A promise that resolves to an instance of OpenAIClient.
   */
  static async getAuthedClient(): Promise<OpenAIClient> {
    const apiKey = await sharedConfig.openaiApiKey;
    const apiOrg = await sharedConfig.openaiApiOrg;
    const configuration = new Configuration({ apiKey, organization: apiOrg });
    const openaiClient = new OpenAIApi(configuration);
    return new OpenAIClient(openaiClient);
  }

  /**
   * Constructs a new instance of the class, initializing it with the provided OpenAIApi client.
   * @param client - An instance of OpenAIApi to be used for API calls.
   */
  constructor(client: OpenAIApi) {
    this.client = client;
  }

  /**
   * Creates a chat completion using the provided parameters and context.
   * The function makes up to three attempts to create the chat completion, with an exponential backoff strategy.
   * It logs the request and response details, and throws an error if the model value is unexpected or if the text response is undefined.
   * The baseTimeoutSeconds is multiplied by (2^n) for each attempt n.
   *
   * @param {Object} args - The arguments for the function.
   * @param {CreateChatCompletionRequest} args.parameters - The parameters for the chat completion request.
   * @param {Object} args.ctx - The context for the request, also used to populate important analytics fields.
   * @param {number} [args.baseTimeoutSeconds=30] - The base timeout in seconds for the request.
   * @param {string} [args.documentId] - The ID of the document, some unique ID for the file/document this OpenAI request is for (for analytics).
   *
   * @returns {Promise<string>} The text response from the chat completion.
   *
   * @throws Will throw an error if the model value is unexpected or if the text response is undefined.
   *
   * @see {@link https://beta.openai.com/docs/api-reference/completions/create}
   */
  async createChatCompletion({
    parameters,
    ctx,
    baseTimeoutSeconds = 30,
    documentId = undefined,
  }: CtxArg & {
    parameters: CreateChatCompletionRequest;
    baseTimeoutSeconds?: number;
    documentId?: string;
  }): Promise<string> {
    // FIXME: This mutates the input
    parameters.messages.unshift({
      role: ChatCompletionRequestMessageRoleEnum.System,
      content: PROMPT_PREFIX,
    });

    const model = modelFromString(parameters.model);
    if (!model) {
      throw new Error(`Unexpected model value ${parameters.model}`);
    }

    const logParams = {
      ...makeRequestLog(parameters),
      openai_request_id: uuidv4(),
    };

    let text: string | undefined;
    const timestampStart = Date.now();
    let completion;

    const maxAttempts = 3;
    for (let i = 0; i < maxAttempts; i += 1) {
      const backoffMs = baseTimeoutSeconds * 2 ** i * 1000;

      try {
        eaveLogger.debug("openai request", ctx, logParams);
        completion = await this.client.createChatCompletion(parameters, {
          timeout: backoffMs,
        }); // timeout in ms
        eaveLogger.debug(
          "openai response",
          logParams,
          makeResponseLog(completion.data),
          ctx,
        );
        text = completion.data.choices[0]?.message?.content;
        break;
      } catch (e: any) {
        // Network error?
        if (i + 1 < maxAttempts) {
          eaveLogger.warning(e, logParams, ctx);
          await new Promise((r) => {
            setTimeout(r, backoffMs);
          });
        } else {
          throw e;
        }
      }
    }

    if (text === undefined) {
      throw new Error("openai text response is undefined");
    }

    const timestampEnd = Date.now();
    const duration_seconds = (timestampEnd - timestampStart) * 1000;
    await logGptRequestData(
      parameters,
      duration_seconds,
      text,
      completion?.request?.usage?.prompt_tokens,
      completion?.request?.usage?.completion_tokens,
      documentId,
      ctx,
    );

    return text;
  }
}

/**
 * Logs the details of a GPT request including the parameters, duration, response, and token counts.
 *
 * @param parameters - The parameters used to create the chat completion request.
 * @param duration_seconds - The duration of the request in seconds.
 * @param response - The response from the GPT.
 * @param input_token_count - The number of tokens in the input prompt. If not provided, it will be calculated.
 * @param output_token_count - The number of tokens in the output response. If not provided, it will be calculated.
 * @param document_id - The ID of the document associated with the request.
 * @param ctx - The logging context.
 *
 * The function will calculate the token count if not provided and log the request using the `logGptRequest` function.
 */
async function logGptRequestData(
  parameters: CreateChatCompletionRequest,
  duration_seconds: number,
  response: string,
  input_token_count?: number,
  output_token_count?: number,
  document_id?: string,
  ctx?: LogContext,
) {
  const fullPrompt = parameters.messages.map((m) => m.content).join("\n");
  const modelEnum = modelFromString(parameters.model);

  if (input_token_count === undefined) {
    input_token_count = costCounter.tokenCount(fullPrompt, modelEnum);
  }
  if (output_token_count === undefined) {
    output_token_count = costCounter.tokenCount(response, modelEnum);
  }

  await logGptRequest(
    {
      feature_name: ctx?.feature_name,
      duration_seconds,
      input_cost_usd: costCounter.calculatePromptCostUSD(
        input_token_count,
        modelEnum,
      ),
      output_cost_usd: costCounter.calculateResponseCostUSD(
        output_token_count,
        modelEnum,
      ),
      input_prompt: fullPrompt,
      output_response: response,
      input_token_count,
      output_token_count,
      model: parameters.model,
      document_id,
    },
    ctx,
  );
}

/**
 * Generates a log of a chat completion response with redacted content.
 *
 * @param {CreateChatCompletionResponse} response - The chat completion response to be logged.
 * @returns {any} An object containing the logged response with redacted content.
 */
function makeResponseLog(response: CreateChatCompletionResponse): any {
  return {
    openai_response: {
      ...(<any>response),
      choices: response.choices.map((c) => ({
        ...c,
        message: {
          ...c.message,
          content: redact(c.message?.content, 100),
        },
      })),
    },
  };
}

/**
 * Creates a log of a chat completion request with redacted content.
 *
 * @param {CreateChatCompletionRequest} request - The chat completion request to be logged.
 * @returns {any} An object containing the logged request with redacted message content.
 */
function makeRequestLog(request: CreateChatCompletionRequest): any {
  return {
    openai_request: {
      ...(<any>request),
      messages: request.messages.map((m) => ({
        ...m,
        content: redact(m.content, 100),
      })),
    },
  };
}
