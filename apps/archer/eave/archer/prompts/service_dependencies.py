from asyncio import sleep
import json
import re
import sys
from eave.archer.config import CONTENT_EXCLUDES
from eave.archer.service_graph import OpenAIResponseService, Service, ServiceGraph, parse_service_response
from eave.archer.service_registry import REGISTRY
from eave.stdlib.exceptions import MaxRetryAttemptsReachedError
import eave.stdlib.openai_client as _o
from eave.archer.util import SHARED_JSON_OUTPUT_INSTRUCTIONS, TOTAL_TOKENS, GithubContext, PROMPT_STORE, get_file_contents, get_lang, get_tokens, make_prompt_content, remove_imports, truncate_file_contents_for_model

_IGNORES_PROMPT = _o.formatprompt(
    """
    Only consider services that are likely to be external to this application. For example, you should not include dependencies on the language's standard libraries, utility functions, things like that.
    """)

async def get_service_references(filepath: str, model: _o.OpenAIModel, github_ctx: GithubContext) -> ServiceGraph | None:
    print("\n\n")
    print(filepath, f"model={model}")

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

    lang = get_lang(filepath)

    system_prompt_lines = []
    user_prompt_lines = []

    user_prompt_lines.append(f"GitHub organization: {github_ctx.org_name}\n")
    user_prompt_lines.append(f"Repository: {github_ctx.repo_name}\n")

    if len(REGISTRY.services) > 0:
        system_prompt_lines.append("You will be given a GitHub organization name, a repository name, a file path to some code in that repository, the code in that file (delimited by three exclamation marks), and a list of known services. Your task is to find which (if any) services are referenced in the code. If a similar service is in the list of known services, use that. Otherwise, create a human-readable name for the service. Your answer will be used to create a high-level system architecture diagram.\n")

        system_prompt_lines.append(f"{_IGNORES_PROMPT}\n")
        system_prompt_lines.append(f"Output your answer as a JSON array of strings, where each string is the name of the service referenced in the code. Each one should exactly match the provided service name. {SHARED_JSON_OUTPUT_INSTRUCTIONS}")

        user_prompt_lines.append("Known services:")
        user_prompt_lines.extend([f"- {s.name}" for s in REGISTRY.services.values()])
        user_prompt_lines.append("") # double newline
    else:
        system_prompt_lines.append("You will be given a GitHub organization name, a repository name, a file path to some code in that repository, and the code in that file (delimited by three exclamation marks). Your task is to find which (if any) services are referenced in the code. Give each service a human-readable name. Your answer will be used to create a high-level system architecture diagram.\n")

        system_prompt_lines.append(f"{_IGNORES_PROMPT}\n")
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

    messages = [
        _o.ChatMessage(role=_o.ChatRole.SYSTEM, content=make_prompt_content(system_prompt_lines)),
        _o.ChatMessage(role=_o.ChatRole.USER, content=make_prompt_content(user_prompt_lines))
    ]

    params = _o.ChatCompletionParameters(
        messages=messages,
        model=model,
        top_p=0.1,
        presence_penalty=-0.1,
        frequency_penalty=-0.1,
    )

    try:
        response = await _o.chat_completion_full_response(params, baseTimeoutSeconds=10)
        assert response
        print(filepath, "response=", response)
        TOTAL_TOKENS["prompt"] += response["usage"]["prompt_tokens"]
        TOTAL_TOKENS["completion"] += response["usage"]["completion_tokens"]
        TOTAL_TOKENS["total"] += response["usage"]["total_tokens"]
    except MaxRetryAttemptsReachedError:
        print(filepath, "WARNING: Max retry attempts reached")
        return None
    except TimeoutError:
        print(filepath, "WARNING: Timeout")
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
