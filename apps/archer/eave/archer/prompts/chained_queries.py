from asyncio import sleep
from dataclasses import dataclass
import json
import os
import re
import sys

from openai.openai_object import OpenAIObject
from eave.archer.config import CONTENT_EXCLUDES, OUTDIR, PROJECT_ROOT, TIMESTAMPF
from eave.archer.service_graph import OpenAIResponseService, Service, ServiceGraph, parse_service_response
from eave.archer.service_registry import SERVICE_REGISTRY
from eave.stdlib.exceptions import MaxRetryAttemptsReachedError
from eave.stdlib.logging import eaveLogger
import eave.stdlib.openai_client as _o
from eave.archer.util import SHARED_JSON_OUTPUT_INSTRUCTIONS, TOTAL_TOKENS, GithubContext, PROMPT_STORE, clean_fpath, get_file_contents, get_lang, get_tokens, make_openai_request, make_prompt_content, remove_imports, truncate_file_contents_for_model

async def query_file_contents_chained(filepath: str, model: _o.OpenAIModel) -> None:
    async def _do_request(messages: list[_o.ChatMessage]) -> str | None:
        params = _o.ChatCompletionParameters(
            messages=messages,
            model=model,
            temperature=0,
            presence_penalty=0,
            frequency_penalty=0,
        )

        response = await make_openai_request(filepath=filepath, params=params)
        if not response:
            return None

        answer = _o.get_choice_content(response)
        if not answer:
            return None

        eaveLogger.info(f"{filepath}\n{answer}")
        return answer



    if model == _o.OpenAIModel.GPT4:
        await sleep(2)

    f = open(f"{OUTDIR}/files.md", "a")
    f.write(f"**{clean_fpath(filepath, prefix=PROJECT_ROOT)}**\n")

    file_contents = get_file_contents(filepath, model=model)
    if not file_contents:
        return None

    code = truncate_file_contents_for_model(file_contents=file_contents, prompt="", model=model)

    messages = [
        _o.ChatMessage(role=_o.ChatRole.USER, content=_o.formatprompt(
            f"""
            Compile a list of external services referenced in this code.

            !!!
            {code}
            !!!
            """
        )),
    ]

    answer = await _do_request(messages)
    f.write(f"```\n{answer}\n```\n")

    f.close()
