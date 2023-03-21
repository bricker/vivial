import assert from 'node:assert';
import { Configuration, OpenAIApi, CreateCompletionRequest } from 'openai';
import appConfig from '../config.js';

export enum OpenAIModel {
  davinciText = 'text-davinci-003',
  davinciCode = 'code-davinci-002',
}

class OpenAIClient {
  private client: OpenAIApi | undefined;

  public async createCompletion(parameters: CreateCompletionRequest): Promise<string> {
    const client = await this.getOpenAIClient();
    const completion = await client.createCompletion(parameters);
    const text = completion.data.choices[0]?.text;
    assert(text !== undefined);
    return text;
  }

  private async getOpenAIClient(): Promise<OpenAIApi> {
    if (this.client !== undefined) {
      return this.client;
    }

    const apiKey = await appConfig.openaiApiKey;
    const configuration = new Configuration({ apiKey });
    this.client = new OpenAIApi(configuration);
    return this.client;
  }
}

const defaultClient = new OpenAIClient();
export default defaultClient;
