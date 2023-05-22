import http
from typing import Any, Optional

import pydantic

from eave.stdlib.util import redact


from .config import shared_config
from .core_api.operations import Status
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import Response
from asgiref.typing import HTTPScope


def status_payload() -> Status.ResponseBody:
    return Status.ResponseBody(
        service=shared_config.app_service,
        version=shared_config.app_version,
        status="OK",
    )


def status_endpoint_starlette(request: Request) -> Response:
    model = status_payload()
    return json_response(model=model)


def status_endpoint_flask() -> str:
    model = status_payload()
    return model.json()


def add_standard_endpoints(app: Any, path_prefix: str = "") -> None:
    app.get(f"{path_prefix}/status")(status_endpoint_flask)


standard_endpoints_starlette = [
    Route("/status", status_endpoint_starlette, methods=["GET", "POST", "HEAD", "OPTIONS", "PUT", "PATCH", "DELETE"])
]


def get_header_value(scope: HTTPScope, name: str) -> str | None:
    """
    This function doesn't support multiple headers with the same name.
    It will always choose the "first" one (from whatever order the ASGI server sent).
    See here for details about the scope["headers"] object:
    https://asgi.readthedocs.io/en/latest/specs/www.html#http-connection-scope
    """
    return next((v.decode() for [n, v] in scope["headers"] if n.decode().lower() == name.lower()), None)


def get_headers(
    scope: HTTPScope, excluded: Optional[list[str]] = None, redacted: Optional[list[str]] = None
) -> dict[str, str]:
    """
    This function doesn't support multiple headers with the same name.
    It will always choose the "first" one (from whatever order the ASGI server sent).
    See here for details about the scope["headers"] object:
    https://asgi.readthedocs.io/en/latest/specs/www.html#http-connection-scope
    """
    if excluded is None:
        excluded = []
    if redacted is None:
        redacted = []

    return {
        n.decode(): (v.decode() if n not in redacted else redact(v.decode())) for [n, v] in scope["headers"] if n not in excluded
    }


def json_response(model: pydantic.BaseModel, status_code: int = http.HTTPStatus.OK) -> Response:
    response = Response(status_code=status_code, content=model.json(), media_type="application/json")
    return response
