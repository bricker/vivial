import enum
import textwrap
from typing import (
    Any,
    List,
    Literal,
    LiteralString,
    Optional,
    Union,
    cast,
)
import uuid

from openai import AsyncOpenAI
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessageParam,
    ChatCompletionToolChoiceOptionParam,
    ChatCompletionToolParam,
)
from openai.types.chat.completion_create_params import Function, FunctionCall, ResponseFormat

from eave.stdlib.logging import LogContext

from ..typing import NOT_GIVEN, JsonObject, NotGiven
from ..config import SHARED_CONFIG
from ..logging import eaveLogger
from ..exceptions import OpenAIDataError


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

_openai_client = AsyncOpenAI(
    api_key=SHARED_CONFIG.eave_openai_api_key,
    organization=SHARED_CONFIG.eave_openai_api_org,
)


async def chat_completion(
    *,
    ctx: Optional[LogContext],
    # document_id: Optional[str] = None,
    messages: list[ChatCompletionMessageParam],
    model: Literal[
        "gpt-4-1106-preview",
        "gpt-4-vision-preview",
        "gpt-4",
        "gpt-4-0314",
        "gpt-4-0613",
        "gpt-4-32k",
        "gpt-4-32k-0314",
        "gpt-4-32k-0613",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k",
        "gpt-3.5-turbo-0301",
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-1106",
        "gpt-3.5-turbo-16k-0613",
    ],
    frequency_penalty: Optional[float] | NotGiven = NOT_GIVEN,
    function_call: FunctionCall | NotGiven = NOT_GIVEN,
    functions: List[Function] | NotGiven = NOT_GIVEN,
    logit_bias: Optional[dict[str, int]] | NotGiven = NOT_GIVEN,
    logprobs: Optional[bool] | NotGiven = NOT_GIVEN,
    max_tokens: Optional[int] | NotGiven = NOT_GIVEN,
    n: Optional[int] | NotGiven = NOT_GIVEN,
    presence_penalty: Optional[float] | NotGiven = NOT_GIVEN,
    response_format: ResponseFormat | NotGiven = NOT_GIVEN,
    seed: Optional[int] | NotGiven = NOT_GIVEN,
    stop: Union[Optional[str], List[str]] | NotGiven = NOT_GIVEN,
    stream: Optional[Literal[False]] | NotGiven = NOT_GIVEN,
    temperature: Optional[float] | NotGiven = NOT_GIVEN,
    tool_choice: ChatCompletionToolChoiceOptionParam | NotGiven = NOT_GIVEN,
    tools: List[ChatCompletionToolParam] | NotGiven = NOT_GIVEN,
    top_logprobs: Optional[int] | NotGiven = NOT_GIVEN,
    top_p: Optional[float] | NotGiven = NOT_GIVEN,
    user: str | NotGiven = NOT_GIVEN,
    **kwargs,
) -> str:
    """
    Makes a request to OpenAI chat completion API, return string response.
    https://beta.openai.com/docs/api-reference/completions/create
    baseTimeoutSeconds is multiplied by (2^n) for each attempt n

    params - main OpenAI API request params
    baseTimeoutSeconds - OpenAI API request timeout
    ctx - log context (also used to populate important analytics fields)
    document_id - some unique ID for the file/document this OpenAI request is for (for analytics)
    returns - API chat completion response string (throws on timeout or other error)
    """

    eave_ctx = LogContext.wrap(ctx)
    openai_request_id = str(uuid.uuid4())
    log_params = {
        "openai_params": kwargs,
        "openai_request_id": openai_request_id,
    }

    eaveLogger.debug(f"OpenAI Request: {openai_request_id}", eave_ctx, log_params)
    # timestamp_start = time.perf_counter()

    # This is crazy but it's basically so we can accurately forward the params from this function to the `completions.create` function.
    createargs: dict[str, Any] = {}
    if frequency_penalty is not NOT_GIVEN:
        createargs["frequency_penalty"] = frequency_penalty
    if function_call is not NOT_GIVEN:
        createargs["function_call"] = function_call
    if functions is not NOT_GIVEN:
        createargs["functions"] = functions
    if logit_bias is not NOT_GIVEN:
        createargs["logit_bias"] = logit_bias
    if logprobs is not NOT_GIVEN:
        createargs["logprobs"] = logprobs
    if max_tokens is not NOT_GIVEN:
        createargs["max_tokens"] = max_tokens
    if n is not NOT_GIVEN:
        createargs["n"] = n
    if presence_penalty is not NOT_GIVEN:
        createargs["presence_penalty"] = presence_penalty
    if response_format is not NOT_GIVEN:
        createargs["response_format"] = response_format
    if seed is not NOT_GIVEN:
        createargs["seed"] = seed
    if stop is not NOT_GIVEN:
        createargs["stop"] = stop
    if stream is not NOT_GIVEN:
        createargs["stream"] = stream
    if temperature is not NOT_GIVEN:
        createargs["temperature"] = temperature
    if tool_choice is not NOT_GIVEN:
        createargs["tool_choice"] = tool_choice
    if tools is not NOT_GIVEN:
        createargs["tools"] = tools
    if top_logprobs is not NOT_GIVEN:
        createargs["top_logprobs"] = top_logprobs
    if top_p is not NOT_GIVEN:
        createargs["top_p"] = top_p
    if user is not NOT_GIVEN:
        createargs["user"] = user

    response: ChatCompletion = await _openai_client.chat.completions.create(**createargs, **kwargs)

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

    candidates = [c for c in response.choices if c.finish_reason == "stop"]

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


def formatprompt(*strings: str) -> str:
    return "\n\n".join([textwrap.dedent(string).strip() for string in strings])
