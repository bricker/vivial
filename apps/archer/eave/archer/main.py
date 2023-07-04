import asyncio
from time import sleep

from .render import render_root_graph
from .config import DIR_EXCLUDES, FILE_INCLUDES, OPENAI_MODEL

from eave.archer.file_contents import get_file_contents, truncate_file_contents_for_model
from eave.archer.service_graph import Service, ServiceGraph, ServiceRegistry
from eave.archer.service_dependencies import get_dependencies
from eave.archer.service_info import get_service_info_from_code

import re
import os

async def run(root_path: str):
    service_registry = ServiceRegistry()
    service = Service(name="Eave")

    for root, dirs, files in os.walk(top=os.path.join(os.environ["EAVE_HOME"])):
        dirs[:] = [d for d in dirs if not any([re.search(e, d) for e in DIR_EXCLUDES])]
        files[:] = [f for f in files if any([re.search(i, f) for i in FILE_INCLUDES])]

        for fname in files:
            sleep(2)

            fpath = os.path.join(root, fname)
            print(fpath)
            file_contents = get_file_contents(fpath)
            file_contents = truncate_file_contents_for_model(file_contents, OPENAI_MODEL)

            if len(file_contents.strip()) == 0:
                print("empty file, skipping")
            else:
                service = await get_service_info_from_code(fpath, file_contents)
                if service:
                    service_registry.register(service)
                    subgraph = await get_dependencies(
                        filepath=fpath,
                        contents=file_contents,
                        registry=service_registry,
                    )
                    if subgraph:
                        service.subgraph.merge(subgraph)

                    graph = service.subgraph

            print("\n\n")

    out = render_root_graph(root_graph)
    print(out)

    with open("graph.mermaid", mode="w+") as f:
        f.write(out)

    print("wrote output to graph.mermaid")

if __name__ == "__main__":
    asyncio.run(run())