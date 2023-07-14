import argparse
import asyncio
from datetime import datetime
import os
import re
from eave.archer.config import PROJECT_ROOT, TIMESTAMP
from eave.archer.graph_builder import build_graph
from eave.archer.prompts.chained_queries import query_file_contents_chained
from eave.archer.prompts.service_dependencies import get_service_references
from eave.archer.service_registry import SERVICE_REGISTRY
from eave.archer.prompts.service_normalization import normalize_services

from eave.archer.render import render_root_graph, write_dependencies, write_file_queries, write_graph, write_hierarchy, write_openai_request, write_run_info, write_services
from eave.archer.service_graph import Service, ServiceGraph
from eave.archer.prompts.service_info import get_services_from_hierarchy

from eave.archer.fs_hierarchy import FSHierarchy, build_hierarchy
from eave.archer.util import GithubContext
from eave.stdlib.openai_client import OpenAIModel

async def run(model: OpenAIModel) -> None:
    root_service = Service(service_name="", service_description="")
    final_services: list[Service] = []
    start_timestamp = TIMESTAMP
    github_ctx = GithubContext(org_name="eave-fyi", repo_name="eave-monorepo")

    try:
        hierarchy = build_hierarchy(root=os.path.join(PROJECT_ROOT, "apps/core"))
        # write_hierarchy(timestamp=start_timestamp, hierarchy=root_hierarchy, model=model)
        await _walk_hierarchy(hierarchy=hierarchy, model=model)

        # final_services = await normalize_services(services=list(SERVICE_REGISTRY.services.values()), model=model)
        # root_service.subgraph.services = final_services
    finally:
        rendered_graph = render_root_graph(graph=root_service.subgraph)
        # write_graph(timestamp=start_timestamp, rendered_graph=rendered_graph)
        # write_file_queries(timestamp=start_timestamp)
        # write_services(timestamp=start_timestamp, services=root_service.subgraph.services)
        # # write_dependencies(timestamp=start_timestamp)
        write_run_info(timestamp=start_timestamp)

async def _walk_hierarchy(hierarchy: FSHierarchy, model: OpenAIModel) -> None:
    for file in hierarchy.files:
        await query_file_contents_chained(filepath=file, model=model)

    for dirh in hierarchy.dirs:
        await _walk_hierarchy(hierarchy=dirh, model=model)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default=OpenAIModel.GPT4.value)
    args = parser.parse_args()
    print(args)

    model = OpenAIModel(value=args.model)
    asyncio.run(run(model))
