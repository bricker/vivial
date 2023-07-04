import json

from .service_dependencies import OUTPUT_INSTRUCTIONS, parse_response
from .render import render_fs_hierarchy
from .config import OPENAI_MODEL
from eave.archer.util import get_filename, get_lang
from eave.archer.service_graph import FSHierarchy, Service
from eave.stdlib.exceptions import MaxRetryAttemptsReachedError
import eave.stdlib.openai_client as _o


_OUTPUT_INSTRUCTIONS = _o.formatprompt(
    """
    Output your answer as a JSON array of objects, with each object containing the following keys:

    - "service_name": the name that you created for the service
    - "service_description": the description that you wrote for the service
    - "service_root": The full path to the directory in the provided hierarchy that can be considered the root directory of the service.

    Your full response should be JSON-parseable, so don't respond with something that can't be parsed by a JSON parser.
    """
)

# async def get_service_name_from_files() -> str:
#     prompt = _o.formatprompt(
#         """
#         The following is a list of filenames, with each file containing some application code.
#         The files are in a directory called {dirname}.
#         Give this directory and group of files a service name
#         """.format(dirname="")
#     )

#     params = _o.ChatCompletionParameters(
#         messages=[
#             prompt
#         ],
#         model=_o.OpenAIModel.GPT_35_TURBO_16K,
#         temperature=0,
#         # frequency_penalty: Optional[float] = None
#         # presence_penalty: Optional[float] = None
#         # temperature: Optional[float] = None
#     )
#     response = await _o.chat_completion(params)
#     assert response
#     print(response)
#     return response

async def get_services_from_repo(hierarchy: FSHierarchy, org_name: str, repo_name: str) -> list[Service] | None:
    rendered_hierarchy = render_fs_hierarchy(hierarchy=hierarchy)
    params = _o.ChatCompletionParameters(
        messages=[
            _o.ChatMessage(role=_o.ChatRole.SYSTEM, content=_o.formatprompt(
                f"""
                You will be provided a GitHub organization name, a repository name, and the directory hierarchy for that repository (starting from the root of the repository). Your task is to create a short, human-readable name and a description for any public HTTP services hosted in this repository. It's likely that there is exactly one service in the repository, however there may be more than one in the case of a monorepo hosting multiple applications, and there may be none in the case of a repository hosting only shared library code, developer tools, configuration, etc.

                The directory hierarchy will be delimited by three exclamation points, and formatted this way:

                - <directory name>
                    - <directory name>
                        - <file name>
                        - <file name>
                    - <directory name>
                        - <file name>
                    - ...

                The service name(s) will be used in a high-level system architecture diagram. Go through the hierarchy a few times before you make your decision, each time refining your understanding of the repository.

                {_OUTPUT_INSTRUCTIONS}
                """
            )),
            _o.ChatMessage(role=_o.ChatRole.USER, content=_o.formatprompt(
                f"""
                GitHub organization: {org_name}

                Repository: {repo_name}

                Directory Hierarchy:
                !!!
                {rendered_hierarchy}
                !!!
                """
            )),
        ],
        model=OPENAI_MODEL,
        temperature=0,
        # frequency_penalty: Optional[float] = None
        # presence_penalty: Optional[float] = None
        # temperature: Optional[float] = None
    )

    try:
        response = await _o.chat_completion(params)
        assert response
        print(response)
        parsed_response = parse_response(response)
    except MaxRetryAttemptsReachedError:
        print("WARNING: Max retry attempts reached")
        return None


    return [Service(**data) for data in parsed_response]
