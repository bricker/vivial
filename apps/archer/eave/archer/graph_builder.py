
from eave.archer.prompts.service_dependencies import get_service_references

from eave.stdlib.openai_client import OpenAIModel
from eave.archer.util import GithubContext
from eave.archer.service_graph import ServiceGraph
from eave.archer.fs_hierarchy import FSHierarchy


async def build_graph(hierarchy: FSHierarchy, model: OpenAIModel, github_ctx: GithubContext) -> ServiceGraph:
    root_graph = ServiceGraph()

    for file in hierarchy.files:
        subgraph = await get_service_references(filepath=file, model=model, github_ctx=github_ctx)
        if subgraph:
            root_graph.merge(subgraph)

    for dirh in hierarchy.dirs:
        subgraph = await build_graph(hierarchy=dirh, model=model, github_ctx=github_ctx)
        root_graph.merge(subgraph)

    return root_graph
