import argparse
import asyncio
from datetime import datetime
import os
import re
from eave.archer.config import PROJECT_ROOT
from eave.archer.graph_builder import build_graph
from eave.archer.prompts.service_dependencies import get_service_references

from eave.archer.render import render_root_graph, write_dependencies, write_graph, write_hierarchy, write_openai_request, write_run_info, write_services
from eave.archer.service_graph import Service, ServiceGraph
from eave.archer.prompts.service_info import get_services_from_hierarchy

from eave.archer.fs_hierarchy import build_hierarchy
from eave.archer.util import GithubContext
from eave.stdlib.openai_client import OpenAIModel

async def run(model: OpenAIModel) -> None:
    root_service = Service(service_name="", service_description="")
    start_timestamp = datetime.now()
    github_ctx = GithubContext(org_name="eave-fyi", repo_name="eave-monorepo")

    try:
        root_hierarchy = build_hierarchy(root=PROJECT_ROOT)
        write_hierarchy(timestamp=start_timestamp, hierarchy=root_hierarchy, model=model)
        await build_graph(hierarchy=root_hierarchy, model=model, github_ctx=github_ctx, parent_service=root_service)

    finally:
        rendered_graph = render_root_graph(graph=root_service.subgraph)
        write_graph(timestamp=start_timestamp, rendered_graph=rendered_graph)
        write_services(timestamp=start_timestamp)
        write_dependencies(timestamp=start_timestamp)
        write_run_info(timestamp=start_timestamp)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default=OpenAIModel.GPT4.value)
    args = parser.parse_args()
    print(args)

    model = OpenAIModel(value=args.model)
    asyncio.run(run(model))
