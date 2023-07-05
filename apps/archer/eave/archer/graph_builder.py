from asyncio import sleep
import sys

from eave.archer.service_dependencies import get_dependencies, get_dependencies_core_services

from eave.stdlib.openai_client import OpenAIModel
from eave.archer.config import OPENAI_MODEL
from eave.archer.util import GithubContext, get_file_contents, truncate_file_contents_for_model
from eave.archer.service_graph import ServiceGraph
from eave.archer.fs_hierarchy import FSHierarchy


async def build_graph(hierarchy: FSHierarchy, github_ctx: GithubContext) -> ServiceGraph:
    root_graph = ServiceGraph()

    for file in hierarchy.files:
        contents = get_file_contents(filepath=file)
        olen = len(contents)
        contents = truncate_file_contents_for_model(contents, OPENAI_MODEL)
        tlen = len(contents)

        if tlen < olen:
            print(f"File contents too long for {OPENAI_MODEL}", f"Original: {olen}", f"Truncated: {tlen}", file, file=sys.stderr)

        if OPENAI_MODEL == OpenAIModel.GPT4:
            await sleep(2)

        print(f"\n\n{file} (len={olen})")
        subgraph = await get_dependencies_core_services(filepath=file, contents=contents, github_ctx=github_ctx)
        if subgraph:
            root_graph.merge(subgraph)

    for dirh in hierarchy.dirs:
        subgraph = await build_graph(hierarchy=dirh, github_ctx=github_ctx)
        root_graph.merge(subgraph)

    return root_graph
