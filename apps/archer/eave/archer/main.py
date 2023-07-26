import argparse
import asyncio
import os
from eave.archer.config import PROJECT_ROOT, TIMESTAMP
from eave.archer.prompts.chained_queries import query_file_contents_chained
from eave.archer.prompts.rolling_summaries import rolling_summary

from eave.archer.render import write_run_info
from eave.archer.service_graph import Service

from eave.archer.fs_hierarchy import build_hierarchy
from eave.archer.util import GithubContext
from eave.stdlib.openai_client import OpenAIModel

async def run(model: OpenAIModel) -> None:
    Service(service_name="", service_description="")
    start_timestamp = TIMESTAMP
    GithubContext(org_name="eave-fyi", repo_name="eave-monorepo")
    hierarchy = build_hierarchy(root=os.path.join(PROJECT_ROOT, "apps/core"))

    try:
        # write_hierarchy(timestamp=start_timestamp, hierarchy=root_hierarchy, model=model)
        await query_file_contents_chained(hierarchy=hierarchy, model=model)
        # await _walk_hierarchy(hierarchy=hierarchy, model=model)

        # final_services = await normalize_services(services=list(SERVICE_REGISTRY.services.values()), model=model)
        # root_service.subgraph.services = final_services
    finally:
        # rendered_graph = render_root_graph(graph=root_service.subgraph)
        # write_graph(timestamp=start_timestamp, rendered_graph=rendered_graph)
        # write_file_queries(timestamp=start_timestamp)
        # write_services(timestamp=start_timestamp, services=root_service.subgraph.services)
        # # write_dependencies(timestamp=start_timestamp)
        write_run_info(timestamp=start_timestamp)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default=OpenAIModel.GPT4.value)
    args = parser.parse_args()
    print(args)

    model = OpenAIModel(value=args.model)
    asyncio.run(run(model))
