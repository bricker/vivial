from typing import Any, Callable

from .config import shared_config
from .core_api.operations import Status

def status_payload() -> dict[str, str]:
    return Status.ResponseBody(
        service=shared_config.app_service,
        version=shared_config.app_version,
        status="OK",
    ).dict()

def add_standard_endpoints(app: Any, path_prefix: str = "") -> None:
    app.get(f"{path_prefix}/status")(status_payload)
