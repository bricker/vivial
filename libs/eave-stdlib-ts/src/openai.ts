import { Configuration, OpenAIApi, CreateChatCompletionRequest, ChatCompletionRequestMessageRoleEnum } from 'openai';
import { sharedConfig } from './config.js';
import eaveLogger from './logging.js';

// eslint-disable-next-line operator-linebreak
export const PROMPT_PREFIX =
  'You are Eave, an AI documentation expert. '
  + "Your job is to write, find, and organize robust, detailed documentation of this organization's information, decisions, projects, and procedures. "
  + "You are responsible for the quality and integrity of this organization's documentation.";

export enum OpenAIModel {
  GPT_35_TURBO = 'gpt-3.5-turbo',
  GPT4 = 'gpt-4',
  GPT4_32K = 'gpt-4-32k',
}

export const MAX_TOKENS: {[key:string]: number} = {
  [OpenAIModel.GPT_35_TURBO]: 4096,
  [OpenAIModel.GPT4]: 8192,
  [OpenAIModel.GPT4_32K]: 32768,
};

export default class OpenAIClient {
  client: OpenAIApi;

  static async getAuthedClient(): Promise<OpenAIClient> {
    const apiKey = await sharedConfig.openaiApiKey;
    const configuration = new Configuration({ apiKey });
    const openaiClient = new OpenAIApi(configuration);
    return new OpenAIClient(openaiClient);
  }

  constructor(client: OpenAIApi) {
    this.client = client;
  }

  async createChatCompletion(parameters: CreateChatCompletionRequest): Promise<string> {
    parameters.messages.unshift({ role: ChatCompletionRequestMessageRoleEnum.System, content: PROMPT_PREFIX });

    const promptLength = parameters.messages.reduce((acc, v) => {
      // eslint-disable-next-line no-param-reassign
      acc += v.content.length;
      return acc;
    }, 0);

    const modelMaxTokens = MAX_TOKENS[parameters.model];
    if (!modelMaxTokens) {
      throw new Error(`Unexpected model value ${parameters.model}`);
    }

    // eslint-disable-next-line no-param-reassign
    parameters.max_tokens = modelMaxTokens - promptLength;
    let text: string | undefined;

    const maxAttempts = 3;
    for (let i = 0; i < maxAttempts; i += 1) {
      try {
        const completion = await this.client.createChatCompletion(parameters, { timeout: 1000 * 10 }); // timeout in ms
        text = completion.data.choices[0]?.message?.content;
      } catch (e: unknown) {
        // Network error?
        if (i < maxAttempts - 1) {
          eaveLogger.warn(e);
          await new Promise((r) => { setTimeout(r, (i + 1) * 1000); });
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
