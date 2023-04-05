import enum
import logging
from dataclasses import asdict, dataclass
from typing import Any, List, LiteralString, Optional, cast

import openai as openai_sdk
import openai.openai_object
import tiktoken

from . import util
from .config import shared_config

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
        "You are able to write a few different types of documentation:\n"

        f"- Technical Documentation: This type of documentation is primarily used by engineers. It might describe how to setup a code repository, how to run tests, troubleshooting of local development environments, bug analysis, or other similar engineering tasks. It can also explain code, systems, architecture, and other engineering concerns.\n"

        f"- Project One-Pager: This type of documentation is used by both product managers and engineers. It might contain information about a project such as an overview, product features, tasks, questions, planning, estimated timeline, stakeholders, team members, and requirements.\n"

        f"- Team Onboarding: This type of documentation is used by all new team members. It might contain information about the current team such as names, profile photos, and job titles. It can also list the team's preferred means of communication (for example, which Slack channels to use for different purposes), meeting schedule, and other information that the new team member needs to know to be successful on the team.\n"

        f"- Engineer Onboarding: This type of documentation is used by engineers who are new to the team. It might contain a list of code repositories that the engineer should clone and setup, a list of requisite or optional software to install and how to install it, a description of the team's git workflow. It may also explain how to procure equipment or software from the company, such as a new keyboard, a different monitor, or a specific IDE.\n"

        "- Other: You can write any other type of documentation, but you prefer the types listed above when appropriate."
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

    def compile(self) -> util.JsonObject:
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


async def chat_completion(params: ChatCompletionParameters) -> Optional[str]:
    """
    https://beta.openai.com/docs/api-reference/completions/create
    """

    ensure_api_key()

    response = await openai_sdk.ChatCompletion.acreate(**params.compile())
    response = cast(openai.openai_object.OpenAIObject, response)
    candidates = [c for c in response.choices if c["finish_reason"] == "stop"]
    choice = candidates[0]

    if len(candidates) < 1:
        logging.warn("No valid choices from openAI; using the first result.")
        choice = response.choices[0]

    assert choice is not None
    answer = str(choice.message.content).strip()
    return answer


# def get_embedding(text, model=OpenAIModel.ADA_EMBEDDING):
#     text = text.replace("\n", " ")
#     return openai.Embedding.create(input=[text], model=model)["data"][0]["embedding"]


# df = pandas.read_csv("output/embedded_1k_reviews.csv")
# df["ada_embedding"] = df.ada_embedding.apply(eval).apply(numpy.array)
# df["ada_embedding"] = df.combined.apply(lambda x: get_embedding(x, model=OpenAIModel.ADA_EMBEDDING))
# df.to_csv("output/embedded_1k_reviews.csv", index=False)
