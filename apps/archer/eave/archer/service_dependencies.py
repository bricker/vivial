import json
import re
import textwrap
from eave.archer.config import OPENAI_MODEL
from .service_graph import Service, ServiceGraph
from .service_registry import ServiceRegistry
from eave.stdlib.exceptions import MaxRetryAttemptsReachedError
import eave.stdlib.openai_client as _o
from eave.archer.util import get_lang

OUTPUT_INSTRUCTIONS = _o.formatprompt(
    """
    Output your answer as a JSON array of objects, with each object containing the following keys:

    - "service_name": the name that you created for the service
    - "service_description": the description that you wrote for the service

    Your full response should be JSON-parseable, so don't respond with something that can't be parsed by a JSON parser.
    """
)

SYSTEM_PROMPT = _o.formatprompt(
    f"""
    You will be given a GitHub organization name, a repository name, and some code from that repository. The code will be delimited by three exclamation marks. Your task is to find the APIs and services that the code depends on, which will then be used to create a high-level system architecture diagram.

    To perform this task, follow these steps:

    1. Find references to well-known, common third-party services in the code. For example, there may be references to Google Cloud, AWS, Redis, Postgres, Slack API, SendGrid.

    2. Find references to internal services. For example: Analytics, Core API, Authentication, Users API, GraphQL, Logging, Storage, Database.

    3. Once you've gone through the code and have a better understanding of its purpose and context, go through it a few more times and adjust your list if necessary based on what you've learned.

    4. For each service, either use one of the provided known service names if it makes sense to do so, otherwise create a short, human-readable name for the service.

    5. Write a 1-paragraph explanation of what the service does and how it fits into the system architecture.

    The code might not have any references to other systems. If you don't think there are any, don't force it.

    {OUTPUT_INSTRUCTIONS}
    """
)

async def get_dependencies(filepath: str, contents: str, registry: ServiceRegistry) -> ServiceGraph | None:
    if len(contents.strip()) == 0:
        return None

    lang = get_lang(filepath) or ""

    # if len(current_services) > 0:
    #     deps_block = _o.formatprompt(
    #         # """
    #         # Use the following list of existing dependencies as a guide, and prefer to use one of these dependencies if it's logical to do so.
    #         # If the dependency or a similar dependency is not in the list, create a new name for it.

    #         # Dependencies:
    #         # ###
    #         # {deps}
    #         # ###
    #         # """.format(
    #         #     deps="\n".join([s.name for s in current_services])
    #         # )
    #     )
    # else:
    #     deps_block = ""

    # (
    #     f"If the following {lang} code has any dependencies on third-party APIs or services, then create a short, human-readable name for each dependency."
    #     "The names will be used in an architecture diagram for an application."
    #     """If there are no dependencies, respond with "none" and nothing else."""
    #     "Format your response as a comma-separated list of each dependency name."
    #     "Respond with only the list and nothing else."
    # ),

    known_service_names = ", ".join([s.name for s in registry.services.values()])
    org_name = "eave-fyi"
    repo_name = "eave-monorepo"
    prompt = _o.formatprompt(
        f"""
        GitHub organization: {org_name}

        Repository: {repo_name}

        Known service names: {known_service_names}

        {lang} Code:
        !!!
        {contents}
        !!!
        """
    )

    params = _o.ChatCompletionParameters(
        messages=[
            _o.ChatMessage(role=_o.ChatRole.SYSTEM, content=SYSTEM_PROMPT),
            prompt,
        ],
        model=OPENAI_MODEL,
        temperature=0,
        # frequency_penalty: Optional[float] = None
        # presence_penalty: Optional[float] = None
        # temperature: Optional[float] = None
    )

    # print(prompt)

    try:
        response = await _o.chat_completion(params)
        assert response
        print(response)
        found_services = parse_response(response)
    except MaxRetryAttemptsReachedError:
        print("WARNING: Max retry attempts reached")
        return None


    subgraph = ServiceGraph()

    for found_service in found_services:
        service = Service(**found_service)
        service = registry.register(service)
        subgraph.add(service)

    return subgraph

def parse_response(response: str) -> list[OpenAIResponseService]:
    return json.loads(response)

async def normalize_services(services: list[OpenAIResponseService]) -> list[OpenAIResponseService]:
    services_list = "\n".join([f"- {s['service_name']}: {s['service_description']}" for s in services])
    print(services_list)

    params = _o.ChatCompletionParameters(
        messages=[
            _o.ChatMessage(role=_o.ChatRole.SYSTEM, content=_o.formatprompt(
                f"""
                You will be provided with an ordered list of API service names and descriptions, which will be used for a system architecture diagram. Some items in the list refer to the same service but were given slightly different names and descriptions.

                Go through the list a few times and reduce it to a list of distinct services by removing services that are duplicates of a service earlier in the list. Two or more services are considered duplicates if their names and descriptions describe the same service, even if the names and descriptions don't perfectly match. When a duplicate is found, keep the one that is more detailed and discard the other one. You may combine the descriptions of the two services to get as much detail as possible, but do not change the name of any service. The names should be considered immutable.

                The provided list will be formatted like this:
                - <service_name>: <service_description>
                - <service_name>: <service_description>
                - <service_name>: <service_description>
                - ...

                {OUTPUT_INSTRUCTIONS}
                """
            )),
            _o.formatprompt(
                f"""
                {services_list}
                """,
            )
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
        reduced_services = parse_response(response)
        return reduced_services
    except MaxRetryAttemptsReachedError:
        print("WARNING: Max retry attempts reached")
        return services
