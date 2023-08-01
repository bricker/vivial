import { v4 as uuidv4 } from 'uuid';
import { Configuration, OpenAIApi, CreateChatCompletionRequest, ChatCompletionRequestMessageRoleEnum } from 'openai';
import { sharedConfig } from '../config.js';
import eaveLogger from '../logging.js';
import { CtxArg } from '../requests.js';
import { modelFromString } from './models.js';

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

  /*
    https://beta.openai.com/docs/api-reference/completions/create
    baseTimeoutSeconds is multiplied by (2^n) for each attempt n
  */
  async createChatCompletion({ parameters, ctx, baseTimeoutSeconds = 30 }: CtxArg & {parameters: CreateChatCompletionRequest, baseTimeoutSeconds?: number}): Promise<string> {
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
    return text;
  }
}
