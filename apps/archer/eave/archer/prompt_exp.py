import asyncio
from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime
import textwrap
import time
from typing import NamedTuple

from asyncio.tasks import sleep

from .util import GithubContext
from .fs_hierarchy import build_hierarchy

from eave.archer.render import clean_fpath, fileout, render_fs_hierarchy, render_root_graph
from eave.archer.config import OPENAI_MODEL, DIR_EXCLUDES, FILE_INCLUDES

from eave.archer.service_graph import Service, ServiceGraph, build_graph
from eave.archer.service_dependencies import get_dependencies
from eave.archer.service_info import get_services_from_repo

import re
import os

from eave.stdlib.openai_client import OpenAIModel

async def run(root_dir: str):
    timestamp = datetime.now()

    root_hierarchy = build_hierarchy(root=root_dir)
    print(render_fs_hierarchy(root_hierarchy))

    github_ctx = GithubContext(
        org_name="eave-fyi",
        repo_name="eave-monorepo"
    )

    services, messages = await get_services_from_repo(
        hierarchy=root_hierarchy,
        github_ctx=github_ctx
    )

    if services:
        root_graph = ServiceGraph()
        for service in services:
            root_graph.add(service)
            hierarchy = build_hierarchy(root=service.root or root_dir)
            await build_graph(hierarchy=hierarchy, service=service)
        rendered_graph = render_root_graph(graph=root_graph)
        fileout(fname="service_info.md", timestamp=timestamp, messages=messages, rendered_graph=rendered_graph)

    for service in services:
        await build_graph(hierarchy=root_hierarchy, graph=service.subgraph)

    rendered_graph = render_root_graph(graph=root_graph)
    fileout(name="service_dependencies.md", messages=messages, rendered_graph=rendered_graph)

if __name__ == "__main__":
    asyncio.run(run(os.path.join(os.environ["EAVE_HOME"], "apps", "slack")))
