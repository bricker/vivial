
from .service_registry import REGISTRY
from .prompts.file_queries import query_file_contents
from eave.archer.prompts.service_dependencies import get_service_references

from eave.stdlib.openai_client import OpenAIModel
from eave.archer.util import GithubContext
from eave.archer.service_graph import Service, ServiceGraph
from eave.archer.fs_hierarchy import FSHierarchy


async def build_graph(hierarchy: FSHierarchy, model: OpenAIModel, github_ctx: GithubContext, parent_service: Service) -> None:
    service = parent_service

    for file in hierarchy.files:
        file_query_response = await query_file_contents(filepath=file, model=model, github_ctx=github_ctx)
        if file_query_response:
            if file_query_response.service_name:
                service = Service(service_name=file_query_response.service_name)
                service = REGISTRY.register(service)

            for ref in file_query_response.third_party_references:
                s = Service(service_name=ref)
                s = REGISTRY.register(s)
                service.subgraph.add(s)


    for dirh in hierarchy.dirs:
        await build_graph(hierarchy=dirh, model=model, github_ctx=github_ctx, parent_service=service)
