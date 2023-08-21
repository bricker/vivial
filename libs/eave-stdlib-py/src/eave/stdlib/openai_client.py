import enum
import textwrap
import time
from dataclasses import asdict, dataclass
from typing import Any, List, LiteralString, Optional, cast
import uuid

import openai as openai_sdk
import openai.error
import openai.openai_object
import tiktoken

from eave.stdlib.logging import LogContext

from .typing import JsonObject
from .config import shared_config
from .logging import eaveLogger
from .exceptions import MaxRetryAttemptsReachedError, OpenAIDataError

tokencoding = tiktoken.get_encoding("gpt2")


class DocumentationType(enum.StrEnum):
    TECHNICAL = "TECHNICAL"
    PROJECT = "PROJECT"
    TEAM_ONBOARDING = "TEAM_ONBOARDING"
    ENGINEER_ONBOARDING = "ENGINEER_ONBOARDING"
    OTHER = "OTHER"


STOP_SEQUENCE = "STOP_SEQUENCE"


class OpenAIModel(enum.StrEnum):
    # ADA_EMBEDDING = "text-embedding-ada-002"
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


def token_count(data: str, model: OpenAIModel) -> int:
    encoder = tiktoken.encoding_for_model(model)
    return len(encoder.encode(data))


class ChatRole(enum.StrEnum):
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"


@dataclass
class ChatMessage:
    role: ChatRole
    content: str


@dataclass
class ChatCompletionParameters:
    messages: List[ChatMessage]
    model: OpenAIModel
    best_of: Optional[int] = None
    n: Optional[int] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    temperature: Optional[float] = None
    stop: Optional[List[str]] = None
    max_tokens: Optional[int] = None

    def compile(self) -> JsonObject:
        params = dict[str, Any]()
        params["model"] = self.model
        params["messages"] = [asdict(m) for m in self.messages]

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
        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens

        if self.stop is not None:
            params["stop"] = self.stop
        else:
            params["stop"] = [STOP_SEQUENCE]

        return params


def ensure_api_key() -> None:
    if openai_sdk.api_key is None:
        openai_sdk.api_key = shared_config.eave_openai_api_key
        openai_sdk.organization = shared_config.eave_openai_api_org


async def chat_completion(
    params: ChatCompletionParameters, baseTimeoutSeconds: int = 30, ctx: Optional[LogContext] = None
) -> Optional[str]:
    """
    https://beta.openai.com/docs/api-reference/completions/create
    baseTimeoutSeconds is multiplied by (2^n) for each attempt n
    """

    ensure_api_key()

    eave_ctx = LogContext.wrap(ctx)
    openai_request_id = str(uuid.uuid4())
    compiled_params = params.compile()
    log_params = {
        "openai_params": compiled_params,
        "openai_request_id": openai_request_id,
    }

    eaveLogger.debug(f"OpenAI Request: {openai_request_id}", eave_ctx, log_params)

    max_attempts = 3
    for i in range(max_attempts):
        backoffSecs = baseTimeoutSeconds * pow(2, i)
        compiled_params["timeout"] = backoffSecs
        backoffSecs = i
        try:
            response = await openai_sdk.ChatCompletion.acreate(**compiled_params)
            try:
                eaveLogger.debug(
                    f"OpenAI Response: {openai_request_id}",
                    {"openai_response": cast(JsonObject, response)},
                    eave_ctx,
                    log_params,
                )
            except Exception as e:
                # Because `reponse` contains Any, we don't want an error if it can't be serialized for GCP
                eaveLogger.exception(e, eave_ctx, log_params)
            break
        except openai.error.OpenAIError as e:
            eaveLogger.warning(e, eave_ctx, log_params)
            if i + 1 < max_attempts:
                time.sleep(backoffSecs)
    else:
        raise MaxRetryAttemptsReachedError("OpenAI")

    response = cast(openai.openai_object.OpenAIObject, response)
    candidates = [c for c in response.choices if c["finish_reason"] == "stop"]

    if len(candidates) > 0:
        choice = candidates[0]
    else:
        eaveLogger.warning(
            f"No valid choices from openAI; using the first result. {openai_request_id}", eave_ctx, log_params
        )
        if len(response.choices) > 0:
            choice = response.choices[0]
        else:
            raise OpenAIDataError("no choices given")

    answer = str(choice.message.content).strip()
    return answer


# def get_embedding(text, model=OpenAIModel.ADA_EMBEDDING):
#     text = text.replace("\n", " ")
#     return openai.Embedding.create(input=[text], model=model)["data"][0]["embedding"]


# df = pandas.read_csv("output/embedded_1k_reviews.csv")
# df["ada_embedding"] = df.ada_embedding.apply(eval).apply(numpy.array)
# df["ada_embedding"] = df.combined.apply(lambda x: get_embedding(x, model=OpenAIModel.ADA_EMBEDDING))
# df.to_csv("output/embedded_1k_reviews.csv", index=False)


def formatprompt(*strings: str) -> str:
    return "\n\n".join([textwrap.dedent(string) for string in strings])
