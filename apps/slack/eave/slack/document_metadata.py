from typing import List
import eave.stdlib.openai_client as eave_openai

async def get_topic(conversation: str) -> str:
    prompt = (
        "Create a short title for the following conversation. Respond with only the title and nothing else.\n\n"
        "The conversation is as follows:\n\n"
        f"{conversation}"
    )

    openai_params = eave_openai.ChatCompletionParameters(
        messages=[prompt],
        n=1,
        frequency_penalty=0,
        presence_penalty=0,
        temperature=0.5,
    )

    openai_response: str | None = await eave_openai.chat_completion(openai_params)
    assert openai_response is not None
    return openai_response

async def get_hierarchy(conversation: str) -> List[str]:
    prompt = (
        "Create a hierarchy of categories at most 3 levels deep, from least specific to most specific, from the following conversation. "
        "If there is more than 1 level, give the answer as a comma-separated list of categories from least specific to most specific.\n\n"
        f"{conversation}"
    )

    openai_params = eave_openai.ChatCompletionParameters(
        messages=[prompt],
        n=1,
        frequency_penalty=0.9,
        presence_penalty=0.9,
        temperature=0,
    )

    answer: str | None = await eave_openai.chat_completion(openai_params)
    assert answer is not None

    parents = list(map(lambda x: x.strip(), reversed(answer.split(","))))
    return parents

async def get_project_title(conversation: str) -> str:
    prompt = (
        f"Is the following conversation about a specific project? If so, what is the name of the project? If not, say: {eave_openai.STOP_SEQUENCE}\n\n"
        f"{conversation}"
    )

    openai_params = eave_openai.ChatCompletionParameters(
        messages=[prompt],
        n=1,
        frequency_penalty=0.9,
        presence_penalty=0.9,
        temperature=0,
    )

    openai_response: str | None = await eave_openai.chat_completion(openai_params)
    assert openai_response is not None
    return openai_response

async def get_documentation_type(conversation: str) -> str:
    prompt = (
        "Which type of documentation is most appropriate for the following conversation?\n\n"
        f"{conversation}\n\n"
    )

    openai_params = eave_openai.ChatCompletionParameters(
        messages=[prompt],
        n=1,
        frequency_penalty=0,
        presence_penalty=0,
        temperature=0,
    )

    openai_response: str | None = await eave_openai.chat_completion(openai_params)
    assert openai_response is not None
    return openai_response

async def get_documentation(conversation: str) -> str:
    prompt = (
        "Create documentation of the information in the following conversation. "
        "You should not simply summarize the conversation; "
        "instead, you should extract information that is important, novel, and is likely to be valuable to other team members in the future. "
        "The documentation should be formatted using plain HTML tags without any inline styling. "
        "The documentation will be embedded into another HTML document, so you should only include HTML tags needed for formatting, and omit tags such as <head>, <body>, <html>, and <!doctype>\n\n"
        f"{conversation}\n\n"
    )

    openai_params = eave_openai.ChatCompletionParameters(
        messages=[prompt],
        n=3,
        frequency_penalty=0.2,
        presence_penalty=0.2,
        temperature=0.5,
    )

    openai_response: str | None = await eave_openai.chat_completion(openai_params)
    assert openai_response is not None
    return openai_response
