import argparse
import asyncio
import os
from datetime import datetime
from eave.archer.config import PROJECT_ROOT
from eave.archer.graph_builder import build_graph

from eave.archer.render import render_fs_hierarchy, render_root_graph, write_graph, write_params
from eave.archer.service_graph import ServiceGraph
from eave.archer.service_info import get_services_from_repo

from eave.archer.fs_hierarchy import build_hierarchy
from eave.archer.util import PROMPT_STORE, GithubContext


async def run():
    start_timestamp = datetime.now()

    root_hierarchy = build_hierarchy(root=PROJECT_ROOT)
    print(render_fs_hierarchy(hierarchy=root_hierarchy))

    github_ctx = GithubContext(org_name="eave-fyi", repo_name="eave-monorepo")

    services = await get_services_from_repo(hierarchy=root_hierarchy, github_ctx=github_ctx)

    root_graph = ServiceGraph()
    for service in [s for s in services if s.root == "apps/slack"]:
        root_graph.add(service)
        # TODO: No need to build the hierarchy twice, share this with the previously built hierarchy
        hierarchy = build_hierarchy(root=service.full_root or root_hierarchy.root)
        subgraph = await build_graph(hierarchy=hierarchy, github_ctx=github_ctx)
        service.subgraph.merge(subgraph)

    rendered_graph = render_root_graph(graph=root_graph)

    try:
        write_graph(timestamp=start_timestamp, rendered_graph=rendered_graph)
        write_params(timestamp=start_timestamp, params=PROMPT_STORE)
    except Exception:
        print(rendered_graph)
        raise

    end_timestamp = datetime.now()
    duration = end_timestamp - start_timestamp
    print(f"Duration: {duration.total_seconds()}")

if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--start-dir', type=str)
    # args = parser.parse_args()
    # print(args)
    asyncio.run(run())
