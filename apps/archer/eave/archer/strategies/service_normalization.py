import json
import re

from eave.stdlib.logging import eaveLogger
from ..service_graph import Service, parse_service_response
from ..util import PROMPT_STORE, SHARED_JSON_OUTPUT_INSTRUCTIONS
import eave.stdlib.openai_client as _o

async def normalize_services(services: list[Service], model: _o.OpenAIModel) -> dict[str, Service]:
    # services_list = "\n".join([f"- {s['service_name']}: {s['service_description']}" for s in services])
    # print(services_list)

    prepared_services = [
        {
            "service_name": s.name,
            "service_description": s.description,
            "dependencies": [d.name for d in s.subgraph.services.values()]
        }
        for s in services
    ]

    prepared_services_json = json.dumps(prepared_services, indent=None)

    params = _o.ChatCompletionParameters(
        messages=[
            _o.ChatMessage(role=_o.ChatRole.SYSTEM, content=_o.formatprompt(
                f"""
                You will be provided with a JSON array of API service names, descriptions, and dependencies.

                Your job is to reduce the list to distinct services by combining similar services. Two or more services are considered duplicates if their names and descriptions describe the same service, even if the names and descriptions don't perfectly match. When duplicates are found, choose an appropriate service name and description, and combine the list of dependencies. If no duplicates are found, the response should be the same as the input.

                The provided JSON array will be formatted like this:

                !!!
                {{"service_name": "...", "service_description": "...", "dependencies": ["...", "..."]}}
                !!!

                The response should be in the same format as the input: A JSON array of objects with the same keys.

                {SHARED_JSON_OUTPUT_INSTRUCTIONS}
                """
            )),
            _o.ChatMessage(role=_o.ChatRole.USER, content=_o.formatprompt(
                f"""
                {prepared_services_json}
                """,
            )),
        ],
        model=model,
        temperature=0,
        # frequency_penalty: Optional[float] = None
        # presence_penalty: Optional[float] = None
        # temperature: Optional[float] = None
    )

    response = await _o.chat_completion(params)
    assert response
    print(response)
    PROMPT_STORE["normalize_services"] = (params, response)
    try:
        parsed = json.loads(response)
    except Exception as e:
        eaveLogger.exception(e)
        parsed = prepared_services

    reduced_services: dict[str, Service] = {}

    for jsvc in parsed:
        service = Service(
            service_name=_normalize_service_name(name=jsvc["service_name"]),
            service_description=jsvc["service_description"]
        )

        for dep in jsvc["dependencies"]:
            depsvc = Service(service_name=dep)
            service.subgraph.add(depsvc)

        reduced_services[service.id] = service

    return reduced_services

def _normalize_service_name(name: str) -> str:
    name = re.sub(r"\(", "", name)
    name = re.sub(r"\)", "", name)
    return name