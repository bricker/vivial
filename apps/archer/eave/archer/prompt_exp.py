import asyncio
from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime
import textwrap
import time
from typing import NamedTuple

from asyncio.tasks import sleep
from .fs_hierarchy import build_hierarchy

from eave.archer.render import clean_fpath, render_fs_hierarchy, render_root_graph
from eave.archer.config import OPENAI_MODEL, DIR_EXCLUDES, FILE_INCLUDES

from eave.archer.file_contents import get_file_contents, truncate_file_contents_for_model
from eave.archer.service_graph import Service, ServiceGraph, ServiceRegistry
from eave.archer.service_dependencies import get_dependencies
from eave.archer.service_info import get_services_from_repo

import re
import os

from eave.stdlib.openai_client import OpenAIModel

async def run(root_dir: str):
    root_hierarchy = build_hierarchy(root=root_dir)
    print(render_fs_hierarchy(root_hierarchy))

    services = await get_services_from_repo(
        hierarchy=root_hierarchy,
        org_name="eave-fyi",
        repo_name="eave-monorepo"
    )

    for service in services:
        await _build_graph(hierarchy=root_hierarchy, graph=service.subgraph)

    rendered_graph = render_root_graph(graph=root_graph)

    dateformat = datetime.now().strftime("%Y-%m-%d--%H:%M:%S")
    outfile=f".out/{dateformat}.md"
    with open(outfile, mode="w+") as f:
        f.write("## Timestamp\n")
        f.write(f"{dateformat}\n\n")
        f.write("## Model\n")
        f.write(OPENAI_MODEL)
        f.write("\n\n## Prompt\n")
        f.write("```")
        f.write(SYSTEM_PROMPT)
        f.write("```\n\n")
        f.write("## Graph\n")
        f.write("```mermaid\n")
        f.write(rendered_graph)
        f.write("\n```")


if __name__ == "__main__":
    asyncio.run(run(os.path.join(os.environ["EAVE_HOME"], "apps", "slack")))
