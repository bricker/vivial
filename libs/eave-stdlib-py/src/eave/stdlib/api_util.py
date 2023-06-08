import http
import re
from typing import Any, Optional

import pydantic
from starlette.middleware import Middleware
from eave.stdlib.headers import AUTHORIZATION_HEADER
from eave.stdlib.middleware.body_parsing import BodyParsingASGIMiddleware
from eave.stdlib.middleware.exception_handling import ExceptionHandlingASGIMiddleware
from eave.stdlib.middleware.logging import LoggingASGIMiddleware
from eave.stdlib.middleware.request_integrity import RequestIntegrityASGIMiddleware

from eave.stdlib.util import redact
import eave.stdlib.core_api.operations.status as status

from .config import shared_config
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import Response
from asgiref.typing import HTTPScope


def status_payload() -> status.Status.ResponseBody:
    return status.Status.ResponseBody(
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

standard_middleware_starlette = [
    Middleware(ExceptionHandlingASGIMiddleware),
    Middleware(RequestIntegrityASGIMiddleware),
    Middleware(BodyParsingASGIMiddleware),
    Middleware(LoggingASGIMiddleware),
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
        n.decode(): (v.decode() if n.decode().lower() not in redacted else redact(v.decode()))
        for [n, v] in scope["headers"]
        if n.decode().lower() not in excluded
    }


def get_bearer_token(scope: HTTPScope) -> str | None:
    auth_header = get_header_value(scope=scope, name=AUTHORIZATION_HEADER)
    if auth_header is None:
        return None

    auth_header_match = re.match("^Bearer (.+)$", auth_header)
    if auth_header_match is None:
        return None

    return auth_header_match.group(1)


def json_response(model: pydantic.BaseModel, status_code: int = http.HTTPStatus.OK) -> Response:
    response = Response(status_code=status_code, content=model.json(), media_type="application/json")
    return response
