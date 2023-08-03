import { encoding_for_model } from 'tiktoken';
import { OpenAIModel } from './models.js';
import eaveLogger from '../logging.js';

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
      eaveLogger.critical(`Model ${model} not found! Cost calculations in BigQuery at risk!`);
      // TODO: is 0 ok?? will logged err get surfaced quickly to devs?
      return 0;
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
      eaveLogger.critical(`Model ${model} not found! Cost calculations in BigQuery at risk!`);
      // TODO: is 0 ok?? will logged err get surfaced quickly to devs?
      return 0;
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
export function calculatePromptCost(prompt: string, model: OpenAIModel): number {
  return (tokenCount(prompt, model) / 1000) * inputTokenCost(model);
}

/**
 * Cost of an output response from the OpenAI api
 * @param prompt
 * @param model
 * @returns float price in USD
 */
export function calculateResponseCost(response: string, model: OpenAIModel): number {
  return (tokenCount(response, model) / 1000) * outputTokenCost(model);
}
