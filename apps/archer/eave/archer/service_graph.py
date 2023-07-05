
import json
import os
import re
from typing import NotRequired, TypedDict

from eave.archer.config import PROJECT_ROOT




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

    def __init__(self, service_name: str = "", service_description: str = "", service_root: str|None = None) -> None:
        self.name = service_name
        self.description = service_description
        self.root = service_root

        self.id = re.sub(r"[^a-z]", "", self.name.lower())
        self.subgraph = ServiceGraph()
        self.visited = False

    @property
    def definition(self) -> str:
        return f"{self.id}({self.name})"

    @property
    def full_root(self) -> str:
        return os.path.join(PROJECT_ROOT, self.root or "")

class ServiceGraph:
    services: dict[str, Service]

    def __init__(self) -> None:
        self.services = {}

    def add(self, service) -> None:
        self.services.setdefault(service.id, service)

    def merge(self, other: "ServiceGraph") -> None:
        self.services.update(other.services)
