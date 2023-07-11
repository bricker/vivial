import argparse
import asyncio
from datetime import datetime
import re
from eave.archer.config import PROJECT_ROOT
from eave.archer.graph_builder import build_graph

from eave.archer.render import render_root_graph, write_graph, write_hierarchy, write_openai_request, write_run_info
from eave.archer.service_graph import ServiceGraph
from eave.archer.prompts.service_info import get_services_from_hierarchy

from eave.archer.fs_hierarchy import build_hierarchy
from eave.archer.util import GithubContext
from eave.stdlib.openai_client import OpenAIModel

async def run(model: OpenAIModel) -> None:
    start_timestamp = datetime.now()

    root_hierarchy = build_hierarchy(root=PROJECT_ROOT)

    github_ctx = GithubContext(org_name="eave-fyi", repo_name="eave-monorepo")

    services = await get_services_from_hierarchy(hierarchy=root_hierarchy, model=model, github_ctx=github_ctx)

    root_graph = ServiceGraph()
    for service in [s for s in services if s.root and re.search(r"^apps/slack", s.root)]:
        root_graph.add(service)
        # TODO: No need to build the hierarchy twice, share this with the previously built hierarchy
        hierarchy = build_hierarchy(root=service.full_root or root_hierarchy.root)
        subgraph = await build_graph(hierarchy=hierarchy, model=model, github_ctx=github_ctx)
        service.subgraph.merge(subgraph)

    rendered_graph = render_root_graph(graph=root_graph)

    try:
        write_hierarchy(timestamp=start_timestamp, hierarchy=root_hierarchy, model=model)
        write_openai_request(timestamp=start_timestamp, filename="services.md", key="get_services")
        write_openai_request(timestamp=start_timestamp, filename="dependencies.md", key="get_dependencies")
        write_graph(timestamp=start_timestamp, rendered_graph=rendered_graph)
        write_run_info(timestamp=start_timestamp)
    except Exception:
        print(rendered_graph)
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default=OpenAIModel.GPT4.value)
    args = parser.parse_args()
    print(args)

    model = OpenAIModel(value=args.model)
    asyncio.run(run(model))
