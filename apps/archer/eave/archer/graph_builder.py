
from .prompts.chained_queries import query_file_contents_chained
from .service_registry import SERVICE_REGISTRY
from .prompts.file_queries import query_file_contents
from eave.archer.prompts.service_dependencies import get_service_references

from eave.stdlib.openai_client import OpenAIModel
from eave.archer.util import GithubContext
from eave.archer.service_graph import Service, ServiceGraph
from eave.archer.fs_hierarchy import FSHierarchy


async def build_graph(hierarchy: FSHierarchy, model: OpenAIModel, github_ctx: GithubContext, parent_service: Service) -> None:
    service = parent_service

    for file in hierarchy.files:
        file_query_response = await query_file_contents_chained(filepath=file, model=model, github_ctx=github_ctx, parent_service=service)
        if file_query_response:
            if file_query_response.service_name:
                service = Service(service_name=file_query_response.service_name, service_description=file_query_response.service_description or "")
                service = SERVICE_REGISTRY.register(service)

            for ref in file_query_response.api_references:
                s = Service(service_name=ref)
                service.subgraph.add(s)


    for dirh in hierarchy.dirs:
        await build_graph(hierarchy=dirh, model=model, github_ctx=github_ctx, parent_service=service)
