import enum
import logging
from dataclasses import asdict, dataclass
from typing import Any, Optional, cast

import openai as openai_sdk
import openai.openai_object
import tiktoken

import eave.internal.settings
import eave.internal.util

tokencoding = tiktoken.get_encoding("gpt2")

PROMPT_PREFIX = (
    "You are Eave, an AI documentation expert. "
    "Your job is to write, find, and organize robust, detailed documentation of this organization's information, decisions, projects, and procedures. "
    "You are responsible for the quality and integrity of this organization's documentation."
)


class OpenAIModel(str, enum.Enum):
    ADA = "text-ada-001"
    ADA_EMBEDDING = "text-embedding-ada-002"
    CURIE = "text-curie-001"
    BABBAGE = "text-babbage-001"
    DAVINCI = "text-davinci-003"


MAX_TOKENS = 4096  # 2048 if using older models


@dataclass
class CompletionParameters:
    prompt: str = ""
    best_of: Optional[int] = None
    n: Optional[int] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    temperature: Optional[float] = None

    def compile(self) -> eave.internal.util.JsonObject:
        params = dict[str, Any]()
        params["prompt"] = self.prompt
        params["model"] = OpenAIModel.DAVINCI
        params["max_tokens"] = MAX_TOKENS - len(tokencoding.encode(self.prompt))

        if self.best_of is not None:
            params["best_of"] = self.best_of
        if self.n is not None:
            params["n"] = self.n
        if self.frequency_penalty is not None:
            params["frequency_penalty"] = self.frequency_penalty
        if self.presence_penalty is not None:
            params["presence_penalty"] = self.presence_penalty
        if self.temperature is not None:
            params["temperature"] = self.temperature
        return params


async def summarize(params: CompletionParameters) -> Optional[str]:
    """
    https://beta.openai.com/docs/api-reference/completions/create
    """

    # Set this here so that the openai key is pulled from GCP Secrets Manager lazily
    if openai_sdk.api_key is None:
        openai_sdk.api_key = eave.internal.settings.APP_SETTINGS.eave_openai_api_key

    response = await openai_sdk.Completion.acreate(**params.compile())
    response = cast(openai.openai_object.OpenAIObject, response)
    candidates = [c for c in response.choices if c["finish_reason"] == "stop"]

    if len(candidates) < 1:
        logging.warn("No valid choices from openAI")
        return None

    answer = str(candidates[0].text).strip()
    return answer


# def get_embedding(text, model=OpenAIModel.ADA_EMBEDDING):
#     text = text.replace("\n", " ")
#     return openai.Embedding.create(input=[text], model=model)["data"][0]["embedding"]


# df = pandas.read_csv("output/embedded_1k_reviews.csv")
# df["ada_embedding"] = df.ada_embedding.apply(eval).apply(numpy.array)
# df["ada_embedding"] = df.combined.apply(lambda x: get_embedding(x, model=OpenAIModel.ADA_EMBEDDING))
# df.to_csv("output/embedded_1k_reviews.csv", index=False)
