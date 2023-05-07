import http
from typing import Any

import pydantic

from .config import shared_config
from .core_api.operations import Status
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse
from asgiref.typing import HTTPScope

def status_endpoint(request: Request) -> JSONResponse:
    model = Status.ResponseBody(
        service=shared_config.app_service,
        version=shared_config.app_version,
        status="OK",
    )

    return json_response(model=model)

def add_standard_endpoints(app: Any, path_prefix: str = "") -> None:
    app.get(f"{path_prefix}/status")(status_endpoint)

standard_endpoints = [
    Route("/status", status_endpoint)
]

def get_header_value(scope: HTTPScope, name: str) -> str | None:
    """
    This function doesn't support multiple headers with the same name.
    It will always choose the "first" one (from whatever order the ASGI server sent).
    See here for details about the scope["headers"] object:
    https://asgi.readthedocs.io/en/latest/specs/www.html#http-connection-scope
    """
    return next((v.decode() for [n, v] in scope["headers"] if n.decode().lower() == name.lower()), None)

def json_response(model: pydantic.BaseModel, status_code: int = http.HTTPStatus.OK) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=model.dict())
