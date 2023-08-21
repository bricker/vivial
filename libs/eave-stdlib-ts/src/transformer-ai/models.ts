export enum OpenAIModel {
  GPT_35_TURBO = 'gpt-3.5-turbo',
  GPT_35_TURBO_16K = 'gpt-3.5-turbo-16k',
  GPT4 = 'gpt-4',
  // GPT4_32K = 'gpt-4-32k',
}

export function modelFromString(v: string): OpenAIModel {
  switch (v) {
    case OpenAIModel.GPT_35_TURBO: return OpenAIModel.GPT_35_TURBO;
    case OpenAIModel.GPT_35_TURBO_16K: return OpenAIModel.GPT_35_TURBO_16K;
    case OpenAIModel.GPT4: return OpenAIModel.GPT4;
    // case OpenAIModel.GPT4_32K: return OpenAIModel.GPT4_32K;
    default: throw new Error(`No OpenAIModel found correlating to ${v}`);
  }
}

type MaxTokens = {
  [OpenAIModel.GPT_35_TURBO]: number;
  [OpenAIModel.GPT_35_TURBO_16K]: number;
  [OpenAIModel.GPT4]: number;
  // [OpenAIModel.GPT4_32K]: number;
}

const MAX_TOKENS: MaxTokens = {
  [OpenAIModel.GPT_35_TURBO]: 4096,
  [OpenAIModel.GPT_35_TURBO_16K]: 16384,
  [OpenAIModel.GPT4]: 8192,
  // [OpenAIModel.GPT4_32K]: 32768,
};

export function maxTokens(model: OpenAIModel): number {
  return MAX_TOKENS[model];
}
