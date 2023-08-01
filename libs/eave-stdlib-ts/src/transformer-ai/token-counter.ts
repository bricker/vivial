import { encoding_for_model } from 'tiktoken';
import { OpenAIModel } from './models.js';
import { Configuration, OpenAIApi, CreateChatCompletionRequest, ChatCompletionRequestMessageRoleEnum } from 'openai';

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
 * @returns float price in USD (rounded to 1e-4 since that is the greatest precision of OpenAI API prices)
 */
export function calculatePromptCost(prompt: string, model: OpenAIModel): number {
  const rawCost = (tokenCount(prompt, model) / 1000) * inputTokenCost(model);
  const precision = 1e4;
  return Math.round(rawCost * precision) / precision;
}

/**
 * Cost of an output response from the OpenAI api
 * @param prompt 
 * @param model 
 * @returns float price in USD (rounded to 1e-4 since that is the greatest precision of OpenAI API prices)
 */
export function calculateResponseCost(response: string, model: OpenAIModel): number {
  const rawCost = (tokenCount(response, model) / 1000) * outputTokenCost(model);
  const precision = 1e4;
  return Math.round(rawCost * precision) / precision;
}
