import enum


class OpenAIModel(enum.StrEnum):
    GPT_35_TURBO = "gpt-3.5-turbo"
    GPT_35_TURBO_16K = "gpt-3.5-turbo-16k"
    GPT4 = "gpt-4"
    # GPT4_32K = "gpt-4-32k"


MAX_TOKENS = {
    OpenAIModel.GPT_35_TURBO: 4096,
    OpenAIModel.GPT_35_TURBO_16K: 16384,
    OpenAIModel.GPT4: 8192,
    # OpenAIModel.GPT4_32K: 32768,
}
