from asyncio import sleep
import json
import re
import sys
from eave.archer.config import CONTENT_EXCLUDES
from eave.archer.service_graph import OpenAIResponseService, Service, ServiceGraph, parse_service_response
from eave.archer.service_registry import REGISTRY
from eave.stdlib.exceptions import MaxRetryAttemptsReachedError
import eave.stdlib.openai_client as _o
from eave.archer.util import SHARED_JSON_OUTPUT_INSTRUCTIONS, TOTAL_TOKENS, GithubContext, PROMPT_STORE, get_file_contents, get_lang, get_tokens, make_prompt_content, truncate_file_contents_for_model

async def get_service_references(filepath: str, model: _o.OpenAIModel, github_ctx: GithubContext) -> ServiceGraph | None:
    print("\n\n")
    print(filepath, f"model={model}")

    if any([re.search(e, filepath) for e in CONTENT_EXCLUDES]):
        print(filepath, "Skipping file due to content exclude.")
        return None

    if model == _o.OpenAIModel.GPT4:
        await sleep(2)

    file_contents = get_file_contents(filepath=filepath)
    filelen = len(file_contents)
    print(filepath, f"filelen={filelen}", f"tokenlen={len(get_tokens(file_contents, model=model))}")

    if len(file_contents.strip()) == 0:
        return None

    lang = get_lang(filepath)

    system_prompt_lines = []
    user_prompt_lines = []

    user_prompt_lines.append(f"GitHub organization: {github_ctx.org_name}\n")
    user_prompt_lines.append(f"Repository: {github_ctx.repo_name}\n")

    if len(REGISTRY.services) > 0:
        system_prompt_lines.append("You will be given a GitHub organization name, a repository name, a file path to some code in that repository, the code in that file (delimited by three exclamation marks), and a list of internal APIs. Your task is to find which (if any) of the provided APIs are referenced in the code. Your answer will be used to create a high-level system architecture diagram.\n")

        system_prompt_lines.append(f"Output your answer as a JSON array of strings, where each string is the name of the service referenced in the code. This should exactly match the provided service name. {SHARED_JSON_OUTPUT_INSTRUCTIONS}")

        user_prompt_lines.append("APIs:")
        user_prompt_lines.extend([f"- {s.name}" for s in REGISTRY.services.values()])
        user_prompt_lines.append("") # double newline
    else:
        system_prompt_lines.append("You will be given a GitHub organization name, a repository name, a file path to some code in that repository, and the code in that file (delimited by three exclamation marks). Your task is to find which (if any) APIs are referenced in the code. Your answer will be used to create a high-level system architecture diagram.\n")

        system_prompt_lines.append(f"Output your answer as a JSON array of strings, where each string is the name of the service referenced in the code. {SHARED_JSON_OUTPUT_INSTRUCTIONS}")

    user_prompt_lines.append(f"File path: {filepath}\n")

    if lang:
        user_prompt_lines.append(f"{lang} Code:")
    else:
        user_prompt_lines.append("Code:")

    current_prompt = "\n".join([make_prompt_content(system_prompt_lines), make_prompt_content(user_prompt_lines)])
    code = truncate_file_contents_for_model(file_contents=file_contents, prompt=current_prompt, model=model)
    trunclen = len(code)

    if trunclen < filelen:
        print(filepath, f"WARNING: File contents too long for {model}", f"filelen={filelen}", f"filetokenlen={len(get_tokens(file_contents, model=model))}", f"trunclen={trunclen}", f"trunctokenlen={len(get_tokens(code, model=model))}", file=sys.stderr)

    user_prompt_lines.append("!!!")
    user_prompt_lines.append(code)
    user_prompt_lines.append("!!!")

    final_prompt = "\n".join([make_prompt_content(system_prompt_lines), make_prompt_content(user_prompt_lines)])

    print(filepath, f"finalpromptlen={len(final_prompt)}", f"finalprompttokenlen={len(get_tokens(final_prompt, model=model))}")

    messages: list[str|_o.ChatMessage] = [
        _o.ChatMessage(role=_o.ChatRole.SYSTEM, content=make_prompt_content(system_prompt_lines)),
        _o.ChatMessage(role=_o.ChatRole.USER, content=make_prompt_content(user_prompt_lines))
    ]

    params = _o.ChatCompletionParameters(
        messages=messages,
        model=model,
        temperature=0,
    )

    try:
        response = await _o.chat_completion_full_response(params)
        assert response
        print(filepath, "response=", response)
        TOTAL_TOKENS["value"] += response["usage"]["total_tokens"]
    except MaxRetryAttemptsReachedError:
        print(filepath, "WARNING: Max retry attempts reached")
        return None

    PROMPT_STORE["get_dependencies"] = (params, response)
    answer = _o.get_choice_content(response)
    assert answer

    found_services = json.loads(answer)
    subgraph = ServiceGraph()

    for found_service in found_services:
        service = Service(service_name=found_service)
        service = REGISTRY.register(service)
        subgraph.add(service)

    return subgraph
