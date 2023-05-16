import enum
import re

from eave.stdlib.exceptions import OpenAIDataError

import eave.stdlib.openai_client as eave_openai
from eave.stdlib import logger

# class MessageType(enum.Enum):
#     REQUEST = "REQUEST"
#     QUESTION = "QUESTION"
#     WATCH = "WATCH"
#     OTHER = "OTHER"
#     UNKNOWN = "UNKNOWN"


class MessageAction(enum.Enum):
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

#     logger.info(f"prompt:\n{prompt}")
#     response = await _get_openai_response(messages=[prompt], temperature=0)
#     logger.info(f"response: {response}")

#     if re.search("request", response, re.IGNORECASE):
#         purpose = MessageType.REQUEST
#     elif re.search("question", response, re.IGNORECASE):
#         purpose = MessageType.QUESTION
#     elif re.search("letting me know", response, re.IGNORECASE):
#         purpose = MessageType.WATCH
#     else:
#         logger.warning(f"Unexpected purpose response: {response}")
#         purpose = MessageType.OTHER

#     logger.info(f"message purpose: {purpose}")
#     return purpose


async def message_action(context: str) -> MessageAction:
    prompt = eave_openai.formatprompt(
        context,
        """
        What action should you take based on this message? Select one of the following choices:
        - Create new documentation
        - Update existing documentation
        - Follow this conversation
        - Stop following this conversation
        - Search for documentation
        - Delete or archive existing documentation
        - No action is needed
        - I don't know
        """,
    )

    logger.info(f"prompt:\n{prompt}")
    response = await _get_openai_response(messages=[prompt], temperature=0)
    logger.info(f"response: {response}")

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
    elif re.search("follow", response, re.IGNORECASE) is not None:
        action = MessageAction.WATCH
    elif re.search("stop following", response, re.IGNORECASE) is not None:
        action = MessageAction.UNWATCH
    elif re.search("no action", response, re.IGNORECASE) is not None:
        action = MessageAction.NONE
    else:
        logger.warning(f"Unexpected message action response: {response}")
        action = MessageAction.UNKNOWN

    logger.info(f"message action: {action}")
    return action


async def _get_openai_response(messages: list[str], temperature: int) -> str:
    params = eave_openai.ChatCompletionParameters(
        messages=messages,
        temperature=temperature,
    )

    openai_completion: str | None = await eave_openai.chat_completion(params)
    if openai_completion is None:
        raise OpenAIDataError()
    return openai_completion
