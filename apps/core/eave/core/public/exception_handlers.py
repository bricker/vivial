from typing import Any, Awaitable, Callable, Mapping
import pydantic
import http
import json
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from .requests import util
import eave.stdlib
import slack_sdk.errors
import sqlalchemy.exc

def not_found(request: Request, exc: Exception) -> Response:
    eave_state = util.get_eave_state(request=request)
    eave.stdlib.logger.error("not found", exc_info=exc, extra=eave_state.log_context)
    status_code = http.HTTPStatus.NOT_FOUND
    content = {
        "status_code": status_code,
        "error": "not found",
        "context": eave_state.log_context,
    }

    return JSONResponse(
        status_code=status_code,
        content=content,
    )


def internal_server_error(request: Request, exc: Exception) -> Response:
    eave_state = util.get_eave_state(request=request)
    eave.stdlib.logger.error("internal server error", exc_info=exc, extra=eave_state.log_context)
    status_code = http.HTTPStatus.INTERNAL_SERVER_ERROR
    content = {
        "status_code": status_code,
        "error": "internal server error",
        "context": eave_state.log_context,
    }

    return JSONResponse(
        status_code=status_code,
        content=content,
    )


def bad_request(request: Request, exc: Exception) -> Response:
    eave_state = util.get_eave_state(request=request)
    eave.stdlib.logger.error("bad request", exc_info=exc, extra=eave_state.log_context)
    status_code = http.HTTPStatus.BAD_REQUEST
    content = {
        "status_code": status_code,
        "error": "bad request",
        "context": eave_state.log_context,
    }

    return JSONResponse(
        status_code=status_code,
        content=content,
    )


def unauthorized(request: Request, exc: Exception) -> Response:
    eave_state = util.get_eave_state(request=request)
    eave.stdlib.logger.error("unauthorized", exc_info=exc, extra=eave_state.log_context)
    status_code = http.HTTPStatus.UNAUTHORIZED
    content = {
        "status_code": status_code,
        "error": "unauthorized",
        "context": eave_state.log_context,
    }

    return JSONResponse(
        status_code=status_code,
        content=content,
    )


def validation_error(request: Request, exc: Exception) -> Response:
    eave_state = util.get_eave_state(request=request)
    eave.stdlib.logger.error("validation error", exc_info=exc, extra=eave_state.log_context)
    status_code = http.HTTPStatus.UNPROCESSABLE_ENTITY
    content = {
        "status_code": status_code,
        "error": "validation errors",
        "context": eave_state.log_context,
    }

    if isinstance(exc, pydantic.ValidationError):
        content["validation_errors"] = exc.json()

    return JSONResponse(
        status_code=status_code,
        content=content,
    )


exception_handlers: Mapping[Any, Callable[[Request, Exception], Response]] = {
    sqlalchemy.exc.NoResultFound: not_found,
    sqlalchemy.exc.MultipleResultsFound: internal_server_error,
    eave.stdlib.exceptions.BadRequestError: bad_request,
    eave.stdlib.exceptions.UnauthorizedError: unauthorized,
    eave.stdlib.exceptions.InternalServerError: internal_server_error,
    pydantic.ValidationError: validation_error,
    slack_sdk.errors.SlackApiError: internal_server_error,
}
