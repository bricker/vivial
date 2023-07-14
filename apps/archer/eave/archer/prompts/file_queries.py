from asyncio import sleep
from dataclasses import dataclass
import json
import re
import sys

from openai.openai_object import OpenAIObject
from eave.archer.config import CONTENT_EXCLUDES, PROJECT_ROOT
from eave.archer.service_graph import OpenAIResponseService, Service, ServiceGraph, parse_service_response
from eave.archer.service_registry import SERVICE_REGISTRY
from eave.stdlib.exceptions import MaxRetryAttemptsReachedError
from eave.stdlib.logging import eaveLogger
import eave.stdlib.openai_client as _o
from eave.archer.util import SHARED_JSON_OUTPUT_INSTRUCTIONS, TOTAL_TOKENS, GithubContext, PROMPT_STORE, clean_fpath, get_file_contents, get_lang, get_tokens, make_prompt_content, remove_imports, truncate_file_contents_for_model

_IGNORES_PROMPT = _o.formatprompt(
    """
    Only consider services that are likely to be external to this application. For example, you should not include dependencies on the language's standard libraries, utility functions, things like that.
    """)

_PREFIX_MESSAGES_SEEKING_SERVICE = [
    _o.ChatMessage(role=_o.ChatRole.SYSTEM, content=_o.formatprompt(
        f"""
        You will be given a GitHub organization name, a repository name, a file path to some code in that repository, and the code in that file (delimited by three exclamation marks). Answer the following questions about the code, and perform the associated tasks:

        1. Is this code setting up an HTTP server framework? If so, create a short, simple, human-readable name for this API, and a short description of the purpose of the API.

        2. Does this code reference or make calls to any other APIs? If so, create a human-readable name for each one, and list them.

        It is very important that the list of APIs only includes ones that are likely to be external to this codebase.

        Examples of HTTP server frameworks:
        - Flask
        - Express
        - Gin
        - Ruby on Rails
        - Django
        - node http
        - Starlette
        - Sinatra
        - Spring

        Examples of valid APIs:
        - OpenAI, Slack, SendGrid, Stripe, Github, etc.
        - Google Cloud, AWS, Azure, etc.
        - Postgres, MySQL, Cloud SQL, Spanner, Redis, etc.
        - Kafka, Beam, Dataflow, etc.
        - Internal Authentication Service
        - Internal Core API

        Examples of invalid APIs:
        - standard libraries
        - package imports
        - utility modules
        - development tooling, ci scripts, etc.

        Format your response as a valid JSON object with the following keys:

        - service_name (String or null): The name that you created for this API, or null if you didn't create one.
        - service_description (String or null): The description that you created for this API, or null if you didn't create one.
        - api_references (String[]): A list of the names you created for any API references in this code. If there are none, this should be an empty array.

        {SHARED_JSON_OUTPUT_INSTRUCTIONS}
        """
    )),
    _o.ChatMessage(role=_o.ChatRole.USER, content=_o.formatprompt(
        """
        Github Organization: eave-fyi
        Repository: eave-core-api
        File path: src/app.py

        python code:
        !!!
        import os
        import eave.stdlib.util
        import logging

        def make_openai_request():
            response = openai.chat_completion(prompt="...")
            eave.stdlib.util.log_analytics(response)
            logging.debug(response)
            return response

        def make_confluence_request():
            response = atlassian.get_confluence_page(id="1")
            eave.stdlib.util.assert_presence(response)
            return response

        app = Starlette(
            routes=[
                Route(path="/user", endpoint=UserEndpoint)
            ]
        )
        !!!
        """
    )),
    _o.ChatMessage(role=_o.ChatRole.ASSISTANT, content=_o.formatprompt(
        """
        {"service_name": "Eave Core API", "service_description": "The Core API service for Eave, providing user information.", "api_references": ["OpenAI", "Confluence"]}
        """
    )),
    _o.ChatMessage(role=_o.ChatRole.USER, content=_o.formatprompt(
        """
        Github Organization: eave-fyi
        Repository: eave-core-api
        File path: src/app.py

        python code:
        !!!
        import os
        import eave.stdlib.util
        import logging
        import redis
        import google.cloud.tasks as tasks

        def cache_set(key, value):
            redis.set(key, value)

        def create_task(payload):
            tasks.create(payload)
        !!!
        """
    )),
    _o.ChatMessage(role=_o.ChatRole.ASSISTANT, content=_o.formatprompt(
        """
        {"service_name": null, "service_description": null, "api_references": ["Redis", "Google Cloud Tasks"]}
        """
    )),
]

_PREFIX_MESSAGES_FOR_FOUND_SERVICE = [
    _o.ChatMessage(role=_o.ChatRole.SYSTEM, content=_o.formatprompt(
        f"""
        You will be given a GitHub organization name, a repository name, a file path to some code in that repository, and the code in that file (delimited by three exclamation marks). Answer the following question about the code, and perform the associated task:

        Does this code reference or make calls to any other APIs? If so, create a human-readable name for each one, and list them.

        It is very important that the list of APIs only includes ones that are likely to be external to this codebase.

        Examples of valid APIs:
        - OpenAI, Slack, SendGrid, Stripe, Github, etc.
        - Google Cloud, AWS, Azure, etc.
        - Postgres, MySQL, Cloud SQL, Spanner, Redis, etc.
        - Kafka, Beam, Dataflow, etc.
        - Internal Authentication Service
        - Internal Core API

        Examples of invalid APIs:
        - standard libraries
        - package imports
        - utility modules
        - development tooling, ci scripts, etc.

        Format your response as a valid JSON object with the following key:

        - api_references (String[]): A list of the names you created for any API references in this code. If there are none, this should be an empty array.

        {SHARED_JSON_OUTPUT_INSTRUCTIONS}
        """
    )),
    _o.ChatMessage(role=_o.ChatRole.USER, content=_o.formatprompt(
        """
        Github Organization: eave-fyi
        Repository: eave-core-api
        File path: src/app.py

        python code:
        !!!
        import os
        import eave.stdlib.util
        import logging

        def make_openai_request():
            response = openai.chat_completion(prompt="...")
            eave.stdlib.util.log_analytics(response)
            logging.debug(response)
            return response

        def make_confluence_request():
            response = atlassian.get_confluence_page(id="1")
            eave.stdlib.util.assert_presence(response)
            return response
        !!!
        """
    )),
    _o.ChatMessage(role=_o.ChatRole.ASSISTANT, content=_o.formatprompt(
        """
        {"api_references": ["OpenAI", "Confluence"]}
        """
    )),
    _o.ChatMessage(role=_o.ChatRole.USER, content=_o.formatprompt(
        """
        Github Organization: eave-fyi
        Repository: eave-core-api
        File path: src/app.py

        python code:
        !!!
        import os
        import eave.stdlib.util
        import logging
        import redis
        import google.cloud.tasks as tasks

        def cache_set(key, value):
            redis.set(key, value)

        def create_task(payload):
            tasks.create(payload)
        !!!
        """
    )),
    _o.ChatMessage(role=_o.ChatRole.ASSISTANT, content=_o.formatprompt(
        """
        {"api_references": ["Redis", "Google Cloud Tasks"]}
        """
    )),
]

@dataclass
class FileQueryResponse:
    api_references: list[str]
    service_name: str | None = None
    service_description: str | None = None

async def query_file_contents(filepath: str, model: _o.OpenAIModel, github_ctx: GithubContext, parent_service: Service | None) -> FileQueryResponse | None:
    print("\n\n")
    print(filepath, f"model={model}")

    if parent_service is None:
        prefix_messages = _PREFIX_MESSAGES_FOR_FOUND_SERVICE
    else:
        prefix_messages = _PREFIX_MESSAGES_SEEKING_SERVICE

    messages = await _build_prompt_for_code_context(filepath=filepath, prefix_messages=prefix_messages, model=model, github_ctx=github_ctx)
    if not messages:
        return None

    params = _o.ChatCompletionParameters(
        messages=messages,
        model=model,
        temperature=0,
        presence_penalty=0,
        frequency_penalty=0,
    )

    response = await _make_openai_request(filepath=filepath, params=params)
    if not response:
        return None

    answer = _o.get_choice_content(response)
    assert answer

    if "file_queries" not in PROMPT_STORE:
        PROMPT_STORE["file_queries"] = []

    PROMPT_STORE["file_queries"].append((params, answer, filepath))

    try:
        parsed_answer = json.loads(answer)
        query_response = FileQueryResponse(**parsed_answer)
        return query_response
    except Exception as e:
        eaveLogger.exception(e)
        return None


async def _load_file(filepath: str, model: _o.OpenAIModel) -> str | None:
    if any([re.search(e, filepath) for e in CONTENT_EXCLUDES]):
        print(filepath, "Skipping file due to content exclude.")
        return None

    if model == _o.OpenAIModel.GPT4:
        await sleep(2)

    file_contents = get_file_contents(filepath=filepath)
    # file_contents = remove_imports(filepath=filepath, contents=file_contents)
    filelen = len(file_contents)
    print(filepath, f"filelen={filelen}", f"tokenlen={len(get_tokens(file_contents, model=model))}")

    if len(file_contents.strip()) == 0:
        return None

    return file_contents

async def _build_prompt_for_code_context(filepath: str, prefix_messages: list[_o.ChatMessage], model: _o.OpenAIModel, github_ctx: GithubContext) -> list[_o.ChatMessage] | None:
    file_contents = await _load_file(filepath, model)
    if not file_contents:
        return None

    user_prompt_lines = []
    user_prompt_lines.append(f"GitHub organization: {github_ctx.org_name}\n")
    user_prompt_lines.append(f"Repository: {github_ctx.repo_name}\n")
    user_prompt_lines.append(f"File path: {clean_fpath(path=filepath, prefix=PROJECT_ROOT)}\n")

    lang = get_lang(filepath)
    if lang:
        user_prompt_lines.append(f"{lang} code:")
    else:
        user_prompt_lines.append("code:")

    prefix_contents = [m.content for m in prefix_messages]
    current_prompt = "\n".join([*prefix_contents, make_prompt_content(user_prompt_lines)])
    code = truncate_file_contents_for_model(file_contents=file_contents, prompt=current_prompt, model=model)
    trunclen = len(code)

    filelen = len(file_contents)
    if trunclen < filelen:
        print(
            filepath,
            f"WARNING: File contents too long for {model}",
            f"filelen={filelen}",
            f"filetokenlen={len(get_tokens(file_contents, model=model))}",
            f"trunclen={trunclen}",
            f"trunctokenlen={len(get_tokens(code, model=model))}",
            file=sys.stderr
        )

    user_prompt_lines.append("!!!")
    user_prompt_lines.append(code)
    user_prompt_lines.append("!!!")

    user_prompt_content = make_prompt_content(user_prompt_lines)
    final_prompt = "\n".join([*prefix_contents, user_prompt_content])
    if not final_prompt:
        return None

    print(
        filepath,
        f"finalpromptlen={len(final_prompt)}",
        f"finalprompttokenlen={len(get_tokens(final_prompt, model=model))}",
    )

    messages = [
        *prefix_messages,
        _o.ChatMessage(role=_o.ChatRole.USER, content=user_prompt_content)
    ]

    return messages

async def _make_openai_request(filepath: str, params: _o.ChatCompletionParameters) -> OpenAIObject | None:
    try:
        response = await _o.chat_completion_full_response(params, baseTimeoutSeconds=10)
        assert response
        print(filepath, "response=", response)
        TOTAL_TOKENS["prompt"] += response["usage"]["prompt_tokens"]
        TOTAL_TOKENS["completion"] += response["usage"]["completion_tokens"]
        TOTAL_TOKENS["total"] += response["usage"]["total_tokens"]
        return response
    except MaxRetryAttemptsReachedError:
        print(filepath, "WARNING: Max retry attempts reached")
        return None
    except TimeoutError:
        print(filepath, "WARNING: Timeout")
        return None
