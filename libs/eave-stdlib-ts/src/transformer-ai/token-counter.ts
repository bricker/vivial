import { encoding_for_model } from 'tiktoken';
import { OpenAIModel } from './models.js';

/**
 * Cost per 1k prompt tokens by model.
 * https://openai.com/pricing
 * @param model
 * @returns float price in USD
 */
function inputTokenCost(model: OpenAIModel): number {
  switch (model) {
    case OpenAIModel.GPT_35_TURBO:
      return 0.0015;
    case OpenAIModel.GPT_35_TURBO_16K:
      return 0.003;
    case OpenAIModel.GPT4:
      return 0.03;
    default:
      throw new Error(`Model ${model} not found to compute token cost!`);
  }
}

/**
 * Cost per 1k response tokens by model.
 * https://openai.com/pricing
 * @param model
 * @returns float price in USD
 */
function outputTokenCost(model: OpenAIModel): number {
  switch (model) {
    case OpenAIModel.GPT_35_TURBO:
      return 0.002;
    case OpenAIModel.GPT_35_TURBO_16K:
      return 0.004;
    case OpenAIModel.GPT4:
      return 0.06;
    default:
      throw new Error(`Model ${model} not found to compute token cost!`);
  }
}

export function tokenCount(data: string, model: OpenAIModel): number {
  const encoder = encoding_for_model(model);
  const count = encoder.encode(data).length;
  encoder.free();
  return count;
}

/**
 * Cost of an input prompt to the OpenAI api
 * @param prompt
 * @param model
 * @returns float price in USD
 */
export function calculatePromptCostUSD(prompt: string, model: OpenAIModel): number {
  return (tokenCount(prompt, model) / 1000) * inputTokenCost(model);
}

/**
 * Cost of an output response from the OpenAI api
 * @param prompt
 * @param model
 * @returns float price in USD
 */
export function calculateResponseCostUSD(response: string, model: OpenAIModel): number {
  return (tokenCount(response, model) / 1000) * outputTokenCost(model);
}
