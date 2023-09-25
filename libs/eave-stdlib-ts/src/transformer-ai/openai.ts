import { ChatCompletionRequestMessageRoleEnum, Configuration, CreateChatCompletionRequest, OpenAIApi } from "openai";
import { v4 as uuidv4 } from "uuid";
import { logGptRequest } from "../analytics.js";
import { sharedConfig } from "../config.js";
import { LogContext, eaveLogger } from "../logging.js";
import { CtxArg } from "../requests.js";
import { modelFromString } from "./models.js";
import * as costCounter from "./token-counter.js";

// eslint-disable-next-line operator-linebreak
export const PROMPT_PREFIX = "You are Eave, a documentation expert. " + "Your job is to write, find, and organize robust, detailed documentation of this organization's information, decisions, projects, and procedures. " + "You are responsible for the quality and integrity of this organization's documentation.";

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

  static async getAuthedClient(): Promise<OpenAIClient> {
    const apiKey = await sharedConfig.openaiApiKey;
    const apiOrg = await sharedConfig.openaiApiOrg;
    const configuration = new Configuration({ apiKey, organization: apiOrg });
    const openaiClient = new OpenAIApi(configuration);
    return new OpenAIClient(openaiClient);
  }

  constructor(client: OpenAIApi) {
    this.client = client;
  }

  /**
   * Makes a request to OpenAI chat completion API.
   * https://beta.openai.com/docs/api-reference/completions/create
   * baseTimeoutSeconds is multiplied by (2^n) for each attempt n
   *
   * @param parameters the main openAI API request params
   * @param ctx log context (also used to populate important analytics fields)
   * @param baseTimeoutSeconds API request timeout
   * @param documentId some unique ID for the file/document this OpenAI request is for (for analytics)
   * @returns API chat completion response string
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
    parameters.messages.unshift({ role: ChatCompletionRequestMessageRoleEnum.System, content: PROMPT_PREFIX });

    const model = modelFromString(parameters.model);
    if (!model) {
      throw new Error(`Unexpected model value ${parameters.model}`);
    }

    const logParams = {
      openai: <any>parameters,
      openaiRequestId: uuidv4(),
    };

    let text: string | undefined;
    const timestampStart = Date.now();
    let completion;

    const maxAttempts = 3;
    for (let i = 0; i < maxAttempts; i += 1) {
      const backoffMs = baseTimeoutSeconds * 2 ** i * 1000;

      try {
        eaveLogger.debug("openai request", ctx, logParams);
        completion = await this.client.createChatCompletion(parameters, { timeout: backoffMs }); // timeout in ms
        eaveLogger.debug("openai response", logParams, { openaiResponse: <any>completion.data }, ctx);
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
    await logGptRequestData(parameters, duration_seconds, text, completion?.request?.usage?.prompt_tokens, completion?.request?.usage?.completion_tokens, documentId, ctx);

    return text;
  }
}

async function logGptRequestData(parameters: CreateChatCompletionRequest, duration_seconds: number, response: string, input_token_count?: number, output_token_count?: number, document_id?: string, ctx?: LogContext) {
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
      input_cost_usd: costCounter.calculatePromptCostUSD(input_token_count, modelEnum),
      output_cost_usd: costCounter.calculateResponseCostUSD(output_token_count, modelEnum),
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
