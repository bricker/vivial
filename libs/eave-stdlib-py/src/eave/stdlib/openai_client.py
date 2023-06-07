import enum
import textwrap
import time
from dataclasses import asdict, dataclass
from typing import Any, List, LiteralString, Optional, cast

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


class DocumentationType(enum.Enum):
    TECHNICAL = "TECHNICAL"
    PROJECT = "PROJECT"
    TEAM_ONBOARDING = "TEAM_ONBOARDING"
    ENGINEER_ONBOARDING = "ENGINEER_ONBOARDING"
    OTHER = "OTHER"


def prompt_prefix() -> LiteralString:
    return (
        "You are Eave, an AI documentation expert. "
        "Your job is to write, find, and organize robust, detailed documentation of this organization's information, decisions, projects, and procedures. "
        "You are responsible for the quality and integrity of this organization's documentation.\n\n"
    )


STOP_SEQUENCE = "STOP_SEQUENCE"


class OpenAIModel(str, enum.Enum):
    # ADA_EMBEDDING = "text-embedding-ada-002"
    GPT_35_TURBO = "gpt-3.5-turbo"
    GPT4 = "gpt-4"
    GPT4_32K = "gpt-4-32k"


MAX_TOKENS = {
    OpenAIModel.GPT_35_TURBO: 4096,
    OpenAIModel.GPT4: 8192,
    OpenAIModel.GPT4_32K: 32768,
}


class ChatRole(str, enum.Enum):
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"


@dataclass
class ChatMessage:
    role: ChatRole
    content: str


@dataclass
class ChatCompletionParameters:
    messages: List[str]
    model: OpenAIModel = OpenAIModel.GPT4
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

        messages = [
            ChatMessage(role=ChatRole.SYSTEM, content=prompt_prefix()),
            *[ChatMessage(role=ChatRole.USER, content=m) for m in self.messages],
        ]

        params["messages"] = [asdict(m) for m in messages]
        # params["max_tokens"] = MAX_TOKENS[self.model] - sum([len(tokencoding.encode(m.content)) for m in messages])

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


async def chat_completion(params: ChatCompletionParameters, ctx: Optional[LogContext] = None) -> Optional[str]:
    """
    https://beta.openai.com/docs/api-reference/completions/create
    """

    ensure_api_key()

    eave_ctx = LogContext.wrap(ctx)
    eaveLogger.debug("OpenAI Request", extra=eave_ctx.set({"openai_request_params": params}))

    max_attempts = 3
    for i in range(max_attempts):
        try:
            response = await openai_sdk.ChatCompletion.acreate(**params.compile())
            try:
                eaveLogger.debug("OpenAI Response", extra=eave_ctx.set({"openai_response": response}))
            except Exception as e:
                # Because `reponse` contains Any, we don't want an error if it can't be serialized for GCP
                eaveLogger.exception("error during logging", extra=eave_ctx.set({"exc": e}))
            break
        except openai.error.RateLimitError as e:
            eaveLogger.warning("OpenAI RateLimitError", exc_info=e, extra=eave_ctx.set({"exc": e}))
            if i + 1 < max_attempts:
                time.sleep(i + 1)
    else:
        raise MaxRetryAttemptsReachedError("OpenAI")

    response = cast(openai.openai_object.OpenAIObject, response)
    candidates = [c for c in response.choices if c["finish_reason"] == "stop"]

    if len(candidates) > 0:
        choice = candidates[0]
    else:
        eaveLogger.warning("No valid choices from openAI; using the first result.", extra=eave_ctx)
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
