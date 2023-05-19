import assert from 'node:assert';
import { Configuration, OpenAIApi, CreateChatCompletionRequest, ChatCompletionRequestMessageRoleEnum } from 'openai';
import { sharedConfig } from './config.js';

// eslint-disable-next-line operator-linebreak
export const PROMPT_PREFIX =
  'You are Eave, an AI documentation expert. '
  + "Your job is to write, find, and organize robust, detailed documentation of this organization's information, decisions, projects, and procedures. "
  + "You are responsible for the quality and integrity of this organization's documentation.";

export enum OpenAIModel {
  GPT_35_TURBO = "gpt-3.5-turbo",
  GPT4 = "gpt-4",
  GPT4_32K = "gpt-4-32k",
}

export const MAX_TOKENS = {
    [OpenAIModel.GPT_35_TURBO]: 4096,
    [OpenAIModel.GPT4]: 8192,
    [OpenAIModel.GPT4_32K]: 32768,
}

export async function createChatCompletion(parameters: CreateChatCompletionRequest): Promise<string> {
  parameters.messages.unshift({ role: ChatCompletionRequestMessageRoleEnum.System, content: PROMPT_PREFIX })

  const client = await getOpenAIClient();
  const completion = await client.createChatCompletion(parameters);
  const text = completion.data.choices[0]?.message?.content;
  assert(text !== undefined);
  return text;
}

let client: OpenAIApi;

async function getOpenAIClient(): Promise<OpenAIApi> {
  if (client !== undefined) {
    return client;
  }

  const apiKey = await sharedConfig.openaiApiKey;
  const configuration = new Configuration({ apiKey });
  client = new OpenAIApi(configuration);
  return client;
}
