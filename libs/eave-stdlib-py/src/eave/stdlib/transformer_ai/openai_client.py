import asyncio
import enum
import textwrap
import time
from dataclasses import asdict, dataclass
from typing import Any, List, LiteralString, Optional, cast
import uuid

import openai as openai_sdk
import openai.error
import openai.openai_object

from eave.stdlib.logging import LogContext
from eave.stdlib.analytics import log_gpt_request

from ..typing import JsonObject
from ..config import shared_config
from ..logging import eaveLogger
from ..exceptions import MaxRetryAttemptsReachedError, OpenAIDataError
from .models import OpenAIModel
from .token_counter import calculate_prompt_cost_usd, calculate_response_cost_usd, token_count


class DocumentationType(enum.StrEnum):
    TECHNICAL = "TECHNICAL"
    PROJECT = "PROJECT"
    TEAM_ONBOARDING = "TEAM_ONBOARDING"
    ENGINEER_ONBOARDING = "ENGINEER_ONBOARDING"
    OTHER = "OTHER"


def prompt_prefix() -> LiteralString:
    return (
        "You are Eave, a documentation expert. "
        "Your job is to write, find, and organize robust, detailed documentation of this organization's information, decisions, projects, and procedures. "
        "You are responsible for the quality and integrity of this organization's documentation.\n\n"
    )


STOP_SEQUENCE = "STOP_SEQUENCE"


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
    messages: List[str]
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

        messages = [
            ChatMessage(role=ChatRole.SYSTEM, content=prompt_prefix()),
            *[ChatMessage(role=ChatRole.USER, content=m) for m in self.messages],
        ]

        params["messages"] = [asdict(m) for m in messages]

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
    params: ChatCompletionParameters,
    baseTimeoutSeconds: int = 30,
    ctx: Optional[LogContext] = None,
) -> str:
    """
    Makes a request to OpenAI chat completion API, return string response.
    https://beta.openai.com/docs/api-reference/completions/create
    baseTimeoutSeconds is multiplied by (2^n) for each attempt n

    params - main OpenAI API request params
    baseTimeoutSeconds - OpenAI API request timeout
    ctx - log context (also used to populate important analytics fields)
    returns - API chat completion response string (throws on timeout or other error)
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
    timestamp_start = time.perf_counter()

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
    timestamp_end = time.perf_counter()
    duration_seconds = round(timestamp_end - timestamp_start)
    await _log_gpt_request(params, answer, duration_seconds, ctx)
    return answer


async def _log_gpt_request(
    params: ChatCompletionParameters,
    response: str,
    duration_seconds: int,
    ctx: Optional[LogContext] = None,
) -> None:
    full_prompt = "\n".join(params.messages)
    prompt_cost = calculate_prompt_cost_usd(full_prompt, params.model)
    response_cost = calculate_response_cost_usd(response, params.model)
    input_tokens = token_count(full_prompt, params.model)
    output_tokens = token_count(response, params.model)

    # openai python client allows for "best_of" parameter, which will generate that many responses,
    # consuming/costing a multiple more response tokens in a single request
    # https://platform.openai.com/docs/api-reference/completions
    if params.best_of:
        response_cost *= params.best_of
        output_tokens *= params.best_of

    await log_gpt_request(
        duration_seconds=duration_seconds,
        input_cost_usd=prompt_cost,
        output_cost_usd=response_cost,
        input_prompt=full_prompt,
        output_response=response,
        input_token_count=input_tokens,
        output_token_count=output_tokens,
        model=params.model,
        ctx=ctx,
    )


def formatprompt(*strings: str) -> str:
    return "\n\n".join([textwrap.dedent(string) for string in strings])
