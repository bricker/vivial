import enum
import re
from typing import Optional

from eave.stdlib.exceptions import OpenAIDataError

import eave.stdlib.openai_client as eave_openai

from eave.stdlib.logging import LogContext, eaveLogger

# I originally had instructions that "Newer messages are more relevant than older messages.", but I don't actually know if that's
# true. Context matters I guess. Something to consider.
CONVO_STRUCTURE = eave_openai.formatprompt(
    """
    The conversation is in ascending chronological order, going from older messages at the top to newer messages at the bottom.
    """
)
# class MessageType(enum.Enum):
#     REQUEST = "REQUEST"
#     QUESTION = "QUESTION"
#     WATCH = "WATCH"
#     OTHER = "OTHER"
#     UNKNOWN = "UNKNOWN"


class MessageAction(enum.StrEnum):
    CREATE_DOCUMENTATION = "CREATE_DOCUMENTATION"
    SEARCH_DOCUMENTATION = "SEARCH_DOCUMENTATION"
    UPDATE_DOCUMENTATION = "UPDATE_DOCUMENTATION"
    REFINE_DOCUMENTATION = "REFINE_DOCUMENTATION"
    DELETE_DOCUMENTATION = "DELETE_DOCUMENTATION"
    WATCH = "WATCH"
    UNWATCH = "UNWATCH"
    NONE = "NONE"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


# async def message_type(context: str) -> MessageType:
#     prompt = eave_openai.formatprompt(f"""
#         {context}

#         What is the purpose of the message? Respond with one of the following choices:
#         1. Making a request
#         2. Asking a question
#         3. Letting me know
#         4. Something else
#     """)

#     eaveLogger.info(f"prompt:\n{prompt}")
#     response = await _get_openai_response(messages=[prompt], temperature=0)
#     eaveLogger.info(f"response: {response}")

#     if re.search("request", response, re.IGNORECASE):
#         purpose = MessageType.REQUEST
#     elif re.search("question", response, re.IGNORECASE):
#         purpose = MessageType.QUESTION
#     elif re.search("letting me know", response, re.IGNORECASE):
#         purpose = MessageType.WATCH
#     else:
#         eaveLogger.warning(f"Unexpected purpose response: {response}")
#         purpose = MessageType.OTHER

#     eaveLogger.info(f"message purpose: {purpose}")
#     return purpose


async def message_action(context: str, ctx: Optional[LogContext] = None) -> MessageAction:
    prompt = eave_openai.formatprompt(
        """
        What action should you take based on the following message? Select one of these choices:
        - Create new documentation
        - Update existing documentation
        - Follow this conversation
        - Stop following this conversation
        - Search, find, or recall some existing documentation or information that you may know
        - Delete or archive existing documentation
        - No action is needed
        - I don't know

        If you're unsure, or if the message is just tagging you to get your attention, then you should choose "Follow this conversation".
        """,
        context,
    )

    eaveLogger.debug(f"prompt:\n{prompt}", ctx)
    response = await _get_openai_response(messages=[prompt], temperature=0)
    eaveLogger.debug(f"response: {response}", ctx)

    response = response.lower()

    if re.search("create", response, re.IGNORECASE) is not None:
        action = MessageAction.CREATE_DOCUMENTATION
    elif re.search("update", response, re.IGNORECASE) is not None:
        action = MessageAction.UPDATE_DOCUMENTATION
    elif re.search("search", response, re.IGNORECASE) is not None:
        action = MessageAction.SEARCH_DOCUMENTATION
    elif (
        re.search("delete", response, re.IGNORECASE) is not None
        or re.search("archive", response, re.IGNORECASE) is not None
    ):
        action = MessageAction.DELETE_DOCUMENTATION
    elif re.search("stop following", response, re.IGNORECASE) is not None:
        action = MessageAction.UNWATCH
    elif re.search("follow", response, re.IGNORECASE) is not None:
        action = MessageAction.WATCH
    elif re.search("no action", response, re.IGNORECASE) is not None:
        action = MessageAction.NONE
    else:
        eaveLogger.warning(f"Unexpected message action response: {response}")
        action = MessageAction.UNKNOWN

    eaveLogger.debug(f"message action: {action}", ctx)
    return action


async def _get_openai_response(messages: list[str], temperature: int) -> str:
    params = eave_openai.ChatCompletionParameters(
        model=eave_openai.OpenAIModel.GPT_35_TURBO_16K,
        messages=messages,
        temperature=temperature,
    )

    openai_completion: str | None = await eave_openai.chat_completion(params)
    if openai_completion is None:
        raise OpenAIDataError()
    return openai_completion
