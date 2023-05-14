import http
from typing import Any, Callable, Mapping

import eave.stdlib
import pydantic
import slack_sdk.errors
import sqlalchemy.exc
from starlette.requests import Request
from starlette.responses import Response

from . import request_state


def not_found(request: Request, exc: Exception) -> Response:
    eave_state = request_state.get_eave_state(request=request)
    eave.stdlib.logger.error("not found", exc_info=exc, extra=eave_state.log_context)

    model = eave.stdlib.core_api.models.ErrorResponse(
        status_code=http.HTTPStatus.NOT_FOUND,
        error_message="not found",
        context=eave_state.public_request_context,
    )
    return eave.stdlib.api_util.json_response(model=model, status_code=model.status_code)


def internal_server_error(request: Request, exc: Exception) -> Response:
    eave_state = request_state.get_eave_state(request=request)
    eave.stdlib.logger.error("internal server error", exc_info=exc, extra=eave_state.log_context)

    model = eave.stdlib.core_api.models.ErrorResponse(
        status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
        error_message="internal server error",
        context=eave_state.public_request_context,
    )

    return eave.stdlib.api_util.json_response(model=model, status_code=model.status_code)


def bad_request(request: Request, exc: Exception) -> Response:
    eave_state = request_state.get_eave_state(request=request)
    eave.stdlib.logger.error("bad request", exc_info=exc, extra=eave_state.log_context)

    model = eave.stdlib.core_api.models.ErrorResponse(
        status_code=http.HTTPStatus.BAD_REQUEST,
        error_message="bad request",
        context=eave_state.public_request_context,
    )

    return eave.stdlib.api_util.json_response(model=model, status_code=model.status_code)


def unauthorized(request: Request, exc: Exception) -> Response:
    eave_state = request_state.get_eave_state(request=request)
    eave.stdlib.logger.error("unauthorized", exc_info=exc, extra=eave_state.log_context)

    model = eave.stdlib.core_api.models.ErrorResponse(
        status_code=http.HTTPStatus.UNAUTHORIZED,
        error_message="unauthorized",
        context=eave_state.public_request_context,
    )

    return eave.stdlib.api_util.json_response(model=model, status_code=model.status_code)


def validation_error(request: Request, exc: Exception) -> Response:
    eave_state = request_state.get_eave_state(request=request)
    eave.stdlib.logger.error("validation error", exc_info=exc, extra=eave_state.log_context)

    if isinstance(exc, pydantic.ValidationError):
        eave_state.public_request_context["validation_errors"] = exc.json()

    model = eave.stdlib.core_api.models.ErrorResponse(
        status_code=http.HTTPStatus.UNPROCESSABLE_ENTITY,
        error_message="validation errors",
        context=eave_state.public_request_context,
    )

    return eave.stdlib.api_util.json_response(model=model, status_code=model.status_code)


exception_handlers: Mapping[Any, Callable[[Request, Exception], Response]] = {
    sqlalchemy.exc.NoResultFound: not_found,
    sqlalchemy.exc.MultipleResultsFound: internal_server_error,
    eave.stdlib.exceptions.BadRequestError: bad_request,
    eave.stdlib.exceptions.UnauthorizedError: unauthorized,
    eave.stdlib.exceptions.InternalServerError: internal_server_error,
    pydantic.ValidationError: validation_error,
    slack_sdk.errors.SlackApiError: internal_server_error,
}
