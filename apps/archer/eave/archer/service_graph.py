
from asyncio import sleep
import json
import re
from typing import NotRequired, Tuple, TypedDict

from .service_registry import REGISTRY

from .service_dependencies import get_dependencies

from .config import OPENAI_MODEL

from .util import GithubContext, clean_fpath, get_file_contents, truncate_file_contents_for_model
from .fs_hierarchy import FSHierarchy
import eave.stdlib.openai_client as _o

class OpenAIResponseService(TypedDict):
    service_name: str
    service_description: str
    service_root: NotRequired[str|None]

def parse_service_response(response: str) -> list[OpenAIResponseService]:
    return json.loads(response)

class Service:
    id: str
    name: str
    description: str
    root: str | None
    subgraph: "ServiceGraph"
    visited: bool

    def __init__(self, service_name: str, service_description: str, service_root: str|None = None) -> None:
        self.name = service_name
        self.description = service_description
        self.root = service_root

        self.id = re.sub(r"[^a-z]", "", self.name.lower())
        self.subgraph = ServiceGraph()
        self.visited = False

    @property
    def definition(self) -> str:
        return f"{self.id}({self.name})"

class ServiceGraph:
    services: dict[str, Service]

    def __init__(self) -> None:
        self.services = {}

    def add(self, service) -> None:
        self.services.setdefault(service.id, service)

    def merge(self, other: "ServiceGraph") -> None:
        self.services.update(other.services)

async def build_graph(hierarchy: FSHierarchy, service: Service, github_ctx: GithubContext) -> None:
    for file in hierarchy.files:
        contents = get_file_contents(filepath=file)
        contents = truncate_file_contents_for_model(contents, OPENAI_MODEL)

        if OPENAI_MODEL == _o.OpenAIModel.GPT4:
            await sleep(2)

        subgraph = await get_dependencies(filepath=file, contents=contents, github_ctx=github_ctx)
        if subgraph:
            service.subgraph.merge(subgraph)

    for dirh in hierarchy.dirs:
        await build_graph(hierarchy=dirh, service=service, github_ctx=github_ctx)