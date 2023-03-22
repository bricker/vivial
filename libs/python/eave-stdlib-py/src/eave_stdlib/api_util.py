from typing import Any
from .config import shared_config
from .core_api.operations import Status

def status_payload() -> str:
    return Status.ResponseBody(
        service=shared_config.app_service,
        version=shared_config.app_version,
        status="OK",
    ).json()

# This would be better than "Any" but I couldn't quite get it working.
# The goal is to accept anything conforming to RouterInterface (eg FastAPI or Flask),
# without having to add those libraries as dependencies to this library.

# class RouterInterface(ABC):
#     @abstractmethod
#     def get(self, rule: str, **options: Any) -> Callable[[Callable[..., Any]], Any]:
#         ...

def add_standard_endpoints(app: Any, path_prefix: str = "") -> None:
    app.get(f"{path_prefix}/status")(status_payload)
