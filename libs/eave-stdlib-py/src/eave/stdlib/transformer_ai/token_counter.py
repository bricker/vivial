import tiktoken

from .models import OpenAIModel


def token_count(data: str, model: OpenAIModel) -> int:
    encoder = tiktoken.encoding_for_model(model)
    return len(encoder.encode(data))


def _input_token_cost(model: OpenAIModel) -> float:
    """
    Cost per 1k prompt tokens by model.
    https://openai.com/pricing

    returns float price in USD
    """
    match (model):
        case OpenAIModel.GPT_35_TURBO:
            return 0.0015
        case OpenAIModel.GPT_35_TURBO_16K:
            return 0.003
        case OpenAIModel.GPT4:
            return 0.03


def _output_token_cost(model: OpenAIModel) -> float:
    """
    Cost per 1k prompt tokens by model.
    https://openai.com/pricing

    returns float price in USD
    """
    match (model):
        case OpenAIModel.GPT_35_TURBO:
            return 0.002
        case OpenAIModel.GPT_35_TURBO_16K:
            return 0.004
        case OpenAIModel.GPT4:
            return 0.06


def calculate_prompt_cost_usd(input_token_count: int, model: OpenAIModel) -> float:
    """
    Cost of an input prompt to the OpenAI api
    returns float price in USD
    """
    return (input_token_count / 1000) * _input_token_cost(model)


def calculate_response_cost_usd(output_token_count: int, model: OpenAIModel) -> float:
    """
    Cost of an output response to the OpenAI api
    returns float price in USD
    """
    return (output_token_count / 1000) * _output_token_cost(model)
