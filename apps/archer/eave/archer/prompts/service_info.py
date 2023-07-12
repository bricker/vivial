
import json
import sys
from eave.archer.fs_hierarchy import FSHierarchy
from eave.archer.render import render_fs_hierarchy
from ..service_registry import REGISTRY
from eave.archer.util import SHARED_JSON_OUTPUT_INSTRUCTIONS, TOTAL_TOKENS, GithubContext, PROMPT_STORE
from eave.archer.service_graph import Service, parse_service_response
from eave.stdlib.exceptions import MaxRetryAttemptsReachedError
import eave.stdlib.openai_client as _o


async def get_services_from_hierarchy(hierarchy: FSHierarchy, model: _o.OpenAIModel, github_ctx: GithubContext) -> list[Service]:
    rendered_hierarchy = render_fs_hierarchy(hierarchy=hierarchy).strip()

    messages: list[_o.ChatMessage] = [
        _o.ChatMessage(role=_o.ChatRole.SYSTEM, content=_o.formatprompt(
            f"""
            You will be provided a GitHub organization name, a repository name, and the directory hierarchy for that repository (starting from the root of the repository). Your task is to create a short, human-readable name and a description for any public services hosted in this repository. It's likely that there is exactly one service in the repository, however there may be more than one in the case of a monorepo hosting multiple applications, and there may be none in the case of a repository hosting only shared library code, developer tools, configuration, etc.

            The directory hierarchy will be delimited by three exclamation marks, and formatted this way:

            - <directory name>
                - <directory name>
                    - <file name>
                    - <file name>
                - <directory name>
                    - <file name>
                - ...

            The service name(s) will be used in a high-level system architecture diagram. Go through the hierarchy a few times before you make your decisions.

            Output your answer as a JSON array of objects, with each object containing the following keys:

            - "service_name": the name that you created for the service
            - "service_description": the description that you wrote for the service
            - "service_root": The path to the root directory for the service.

            {SHARED_JSON_OUTPUT_INSTRUCTIONS}
            """
        )),
        _o.ChatMessage(role=_o.ChatRole.USER, content=_o.formatprompt(
            f"""
            GitHub organization: {github_ctx.org_name}

            Repository: {github_ctx.repo_name}

            Directory hierarchy:
            !!!
            """,
            rendered_hierarchy,
            "!!!",
        )),
    ]

    params = _o.ChatCompletionParameters(
        messages=messages,
        model=model,
        top_p=0.1,
        presence_penalty=0,
        frequency_penalty=0,
    )


    try:
        response = await _o.chat_completion_full_response(params)
        assert response
        print(response)
        TOTAL_TOKENS["prompt"] += response["usage"]["prompt_tokens"]
        TOTAL_TOKENS["completion"] += response["usage"]["completion_tokens"]
        TOTAL_TOKENS["total"] += response["usage"]["total_tokens"]
    except MaxRetryAttemptsReachedError:
        print("WARNING: Max retry attempts reached", file=sys.stderr)
        return []

    PROMPT_STORE["get_services"] = (params, response)

    answer = _o.get_choice_content(response)
    assert answer

    parsed_response = parse_service_response(answer)
    services = [Service(**data) for data in parsed_response]
    for service in services:
        REGISTRY.register(service)
    return services
