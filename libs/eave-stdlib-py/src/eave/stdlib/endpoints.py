from eave.stdlib.api_util import json_response
import eave.stdlib.core_api.operations.status as status
import eave.stdlib.cache

from .config import shared_config
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import Response


def status_payload() -> status.Status.ResponseBody:
    return status.Status.ResponseBody(
        service=shared_config.app_service,
        version=shared_config.app_version,
        status="OK",
    )
