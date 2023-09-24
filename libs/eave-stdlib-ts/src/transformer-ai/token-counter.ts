import { encoding_for_model } from "tiktoken";
import { OpenAIModel } from "./models.js";

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
      // using 'never' typed constant here to typecheck that a case hasnt been missed
      // eslint-disable-next-line no-case-declarations
      const missedCase: never = model;
      throw new Error(`Model ${missedCase} not found to compute token cost!`);
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
      // using 'never' typed constant here to typecheck that a case hasnt been missed
      // eslint-disable-next-line no-case-declarations
      const missedCase: never = model;
      throw new Error(`Model ${missedCase} not found to compute token cost!`);
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
 * @param inputTokenCount number of tokens input to model
 * @param model
 * @returns float price in USD
 */
export function calculatePromptCostUSD(inputTokenCount: number, model: OpenAIModel): number {
  return (inputTokenCount / 1000) * inputTokenCost(model);
}

/**
 * Cost of an output response from the OpenAI api
 * @param outputTokenCount number of tokens output from model
 * @param model
 * @returns float price in USD
 */
export function calculateResponseCostUSD(outputTokenCount: number, model: OpenAIModel): number {
  return (outputTokenCount / 1000) * outputTokenCost(model);
}
