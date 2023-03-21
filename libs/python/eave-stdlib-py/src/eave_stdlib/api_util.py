from abc import ABC, abstractmethod
from typing import Any, Callable
from .util import JsonObject
from .config import shared_config

def status_payload() -> JsonObject:
    return {
        "service": shared_config.app_service,
        "version": shared_config.app_version,
        "status": "OK",
    }

class RouterInterface(ABC):
    @abstractmethod
    def get(self, rule: str, **options: Any) -> Callable[[Callable[..., Any]], Any]:
        ...

def add_standard_endpoints(app: RouterInterface, path_prefix: str = ""):
    app.get(f"{path_prefix}/status")(status_payload)
