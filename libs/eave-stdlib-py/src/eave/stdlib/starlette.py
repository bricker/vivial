import http
from collections.abc import Callable, Mapping
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from eave.stdlib.http_exceptions import HTTPError
from eave.stdlib.logging import LOGGER


def _make_error_response(http_status: http.HTTPStatus) -> JSONResponse:
    return JSONResponse(
        content={
            "status_code": http_status.value,
            "message": http_status.phrase,
        },
        status_code=http_status.value,
    )


def internal_server_error(request: Request, exc: Exception) -> Response:
    LOGGER.exception(exc)
    return _make_error_response(http.HTTPStatus.INTERNAL_SERVER_ERROR)


def http_error_handler(request: Request, exc: Exception) -> Response:
    LOGGER.exception(exc)

    if isinstance(exc, HTTPError):
        # We intentionally don't use the original exception's message here,
        # because we want the response message to be generic.
        return _make_error_response(exc.status_code)
    else:
        return _make_error_response(http.HTTPStatus.INTERNAL_SERVER_ERROR)


exception_handlers: Mapping[Any, Callable[[Request, Exception], Response]] = {
    HTTPError: http_error_handler,
    # This special case is used by Starlette for the ServerErrorMiddleware, which always re-raises the error.
    # This generic handler allows us to define our own Internal Server Error response.
    Exception: internal_server_error,
}
