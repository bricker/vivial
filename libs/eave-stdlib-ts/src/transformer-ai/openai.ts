import { v4 as uuidv4 } from 'uuid';
import { Configuration, OpenAIApi, CreateChatCompletionRequest, ChatCompletionRequestMessageRoleEnum } from 'openai';
import { sharedConfig } from '../config.js';
import eaveLogger, { LogContext } from '../logging.js';
import { CtxArg } from '../requests.js';
import { modelFromString } from './models.js';
import { logGptRequest } from '../analytics.js';
import * as costCounter from './token-counter.js';

// eslint-disable-next-line operator-linebreak
export const PROMPT_PREFIX =
  'You are Eave, a documentation expert. '
  + "Your job is to write, find, and organize robust, detailed documentation of this organization's information, decisions, projects, and procedures. "
  + "You are responsible for the quality and integrity of this organization's documentation.";

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
   * @returns API chat completion response string
   */
  async createChatCompletion({
    parameters,
    ctx,
    baseTimeoutSeconds = 30,
  }: CtxArg & {
    parameters: CreateChatCompletionRequest,
    baseTimeoutSeconds?: number,
    file_log_id?: string | undefined,
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

    const maxAttempts = 3;
    for (let i = 0; i < maxAttempts; i += 1) {
      const backoffMs = baseTimeoutSeconds * (2 ** i) * 1000;
      try {
        eaveLogger.debug('openai request', ctx, logParams);
        const completion = await this.client.createChatCompletion(parameters, { timeout: backoffMs }); // timeout in ms
        eaveLogger.debug('openai response', logParams, { openaiResponse: <any>completion.data }, ctx);
        text = completion.data.choices[0]?.message?.content;
        break;
      } catch (e: any) {
        // Network error?
        if (i + 1 < maxAttempts) {
          eaveLogger.warning(e, logParams, ctx);
          await new Promise((r) => { setTimeout(r, backoffMs); });
        } else {
          throw e;
        }
      }
    }

    if (text === undefined) {
      throw new Error('openai text response is undefined');
    }

    const timestampEnd = Date.now();
    const duration_seconds = (timestampEnd - timestampStart) * 1000;
    await logGptRequestData(parameters, text, duration_seconds, ctx);

    return text;
  }
}

async function logGptRequestData(
  parameters: CreateChatCompletionRequest,
  response: string,
  duration_seconds: number,
  ctx?: LogContext | undefined,
) {
  const fullPrompt = Object.values(parameters.messages).join('\n');
  const modelEnum = modelFromString(parameters.model)!;

  await logGptRequest({
    feature_name: ctx?.feature_name,
    duration_seconds,
    input_cost_usd: costCounter.calculatePromptCostUSD(fullPrompt, modelEnum),
    output_cost_usd: costCounter.calculateResponseCostUSD(response, modelEnum),
    input_prompt: fullPrompt,
    output_response: response,
    input_token_count: costCounter.tokenCount(fullPrompt, modelEnum),
    output_token_count: costCounter.tokenCount(response, modelEnum),
    model: parameters.model,
  }, ctx);
}
