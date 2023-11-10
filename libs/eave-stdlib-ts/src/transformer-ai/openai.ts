import OpenAI from "openai";
import {
  ChatCompletion,
  ChatCompletionCreateParamsNonStreaming,
  ChatCompletionMessageParam,
} from "openai/resources/chat/completions.js";
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
  client: OpenAI;

  static async getAuthedClient(): Promise<OpenAIClient> {
    const apiKey = await sharedConfig.openaiApiKey;
    const apiOrg = await sharedConfig.openaiApiOrg;
    const openai = new OpenAI({ apiKey, organization: apiOrg });
    return new OpenAIClient(openai);
  }

  constructor(client: OpenAI) {
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
    parameters: ChatCompletionCreateParamsNonStreaming;
    baseTimeoutSeconds?: number;
    documentId?: string;
  }): Promise<string> {
    const messages: ChatCompletionMessageParam[] = [
      {
        role: "system",
        content: PROMPT_PREFIX,
      },
      ...parameters.messages,
    ];

    parameters = { ...parameters, messages };

    const model = modelFromString(parameters.model);
    if (!model) {
      throw new Error(`Unexpected model value ${parameters.model}`);
    }

    const logParams = {
      ...makeRequestLog(parameters),
      openai_request_id: uuidv4(),
    };

    let text: string | null | undefined;
    const timestampStart = Date.now();
    let completion: ChatCompletion | undefined;

    const maxAttempts = 3;
    for (let i = 0; i < maxAttempts; i += 1) {
      const backoffMs = baseTimeoutSeconds * 2 ** i * 1000;

      try {
        eaveLogger.debug("openai request", ctx, logParams);
        completion = await this.client.chat.completions.create(parameters, {
          timeout: backoffMs,
        }); // timeout in ms
        eaveLogger.debug(
          "openai response",
          logParams,
          makeResponseLog(completion),
          ctx,
        );
        text = completion.choices[0]?.message?.content;
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

    if (text === undefined || text === null) {
      throw new Error("openai text response is undefined");
    }

    const timestampEnd = Date.now();
    const duration_seconds = (timestampEnd - timestampStart) / 1000;
    await logGptRequestData(
      parameters,
      duration_seconds,
      text,
      completion?.usage?.prompt_tokens,
      completion?.usage?.completion_tokens,
      documentId,
      ctx,
    );

    return text;
  }
}

async function logGptRequestData(
  parameters: ChatCompletionCreateParamsNonStreaming,
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

function makeResponseLog(response: ChatCompletion): any {
  return {
    openai_response: {
      ...(<any>response),
      choices: response.choices.map((c) => ({
        ...c,
        message: {
          ...c.message,
          content: redact(c.message.content, 100),
        },
      })),
    },
  };
}

function makeRequestLog(request: ChatCompletionCreateParamsNonStreaming): any {
  return {
    openai_request: {
      ...(<any>request),
      messages: request.messages.map((m) => {
        return {
          ...m,
          content: redact(m.content?.toString(), 100),
        };
      }),
    },
  };
}
