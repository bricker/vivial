
import re
from typing import NotRequired, TypedDict
import eave.stdlib.openai_client as _o

class OpenAIResponseService(TypedDict):
    service_name: str
    service_description: str
    service_root: NotRequired[str|None]

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

async def build_graph(hierarchy: FSHierarchy, graph: ServiceGraph) -> None:
    for file in hierarchy.files:
        print(clean_fpath(file))
        contents = get_file_contents(filepath=file)
        contents = truncate_file_contents_for_model(contents, OPENAI_MODEL)

        if OPENAI_MODEL == OpenAIModel.GPT4:
            await sleep(2)

        service = Service(service_name=clean_fpath(file), service_description="a file")
        subgraph = await get_dependencies(filepath=file, contents=contents, registry=_REGISTRY)
        if subgraph:
            service.subgraph.merge(subgraph)

        print("\n")

    for dirh in hierarchy.dirs:
        await build_graph(hierarchy=dirh, graph=graph)