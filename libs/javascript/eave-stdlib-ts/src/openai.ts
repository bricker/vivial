import assert from 'node:assert';
import { Configuration, OpenAIApi, CreateCompletionRequest } from 'openai';
import { sharedConfig } from './config';

// eslint-disable-next-line operator-linebreak
export const PROMPT_PREFIX =
  'You are Eave, an AI documentation expert. '
  + "Your job is to write, find, and organize robust, detailed documentation of this organization's information, decisions, projects, and procedures. "
  + "You are responsible for the quality and integrity of this organization's documentation.";

export enum OpenAIModel {
  davinciText = 'text-davinci-003',
  davinciCode = 'code-davinci-002',
}

export async function createCompletion(parameters: CreateCompletionRequest): Promise<string> {
  const client = await getOpenAIClient();
  const completion = await client.createCompletion(parameters);
  const text = completion.data.choices[0]?.text;
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
