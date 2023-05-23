import http
from typing import Any, Callable, Mapping

import eave.stdlib
import pydantic
from starlette.requests import Request
from starlette.responses import Response

from eave.stdlib import request_state
from eave.stdlib.logging import eaveLogger


def internal_server_error(request: Request, exc: Exception) -> Response:
    eave_state = request_state.get_eave_state(request=request)
    eaveLogger.exception(exc, stack_info=True, extra=eave_state.log_context)

    model = eave.stdlib.core_api.models.ErrorResponse(
        status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
        error_message=http.HTTPStatus.INTERNAL_SERVER_ERROR.phrase,
        context=eave_state.public_request_context,
    )

    return eave.stdlib.api_util.json_response(model=model, status_code=model.status_code)


def not_found(request: Request, exc: Exception) -> Response:
    eave_state = request_state.get_eave_state(request=request)
    # FIXME: This log message is bad
    eaveLogger.warning(http.HTTPStatus.NOT_FOUND, exc_info=exc, extra=eave_state.log_context)

    model = eave.stdlib.core_api.models.ErrorResponse(
        status_code=http.HTTPStatus.NOT_FOUND,
        error_message=http.HTTPStatus.NOT_FOUND.phrase,
        context=eave_state.public_request_context,
    )

    return eave.stdlib.api_util.json_response(model=model, status_code=model.status_code)


def bad_request(request: Request, exc: Exception) -> Response:
    eave_state = request_state.get_eave_state(request=request)
    # FIXME: This log message is bad
    eaveLogger.warning(http.HTTPStatus.BAD_REQUEST, exc_info=exc, extra=eave_state.log_context)

    model = eave.stdlib.core_api.models.ErrorResponse(
        status_code=http.HTTPStatus.BAD_REQUEST,
        error_message=http.HTTPStatus.BAD_REQUEST.phrase,
        context=eave_state.public_request_context,
    )

    return eave.stdlib.api_util.json_response(model=model, status_code=model.status_code)


def unauthorized(request: Request, exc: Exception) -> Response:
    eave_state = request_state.get_eave_state(request=request)
    eaveLogger.warning(
        "Authentication error occurred. The client will be logged out.", exc_info=exc, extra=eave_state.log_context
    )

    model = eave.stdlib.core_api.models.ErrorResponse(
        status_code=http.HTTPStatus.UNAUTHORIZED,
        error_message=http.HTTPStatus.UNAUTHORIZED.phrase,
        context=eave_state.public_request_context,
    )
    response = eave.stdlib.api_util.json_response(model=model, status_code=model.status_code)
    eave.stdlib.cookies.delete_auth_cookies(response=response)
    return response


def validation_error(request: Request, exc: Exception) -> Response:
    eave_state = request_state.get_eave_state(request=request)
    eaveLogger.warning("validation error", exc_info=exc, extra=eave_state.log_context)

    if isinstance(exc, pydantic.ValidationError):
        eave_state.public_request_context["validation_errors"] = exc.json()

    model = eave.stdlib.core_api.models.ErrorResponse(
        status_code=http.HTTPStatus.UNPROCESSABLE_ENTITY,
        error_message="validation errors",
        context=eave_state.public_request_context,
    )

    return eave.stdlib.api_util.json_response(model=model, status_code=model.status_code)


exception_handlers: Mapping[Any, Callable[[Request, Exception], Response]] = {
    # eave.stdlib.exceptions.NotFoundError: not_found,
    # eave.stdlib.exceptions.BadRequestError: bad_request,
    # eave.stdlib.exceptions.UnauthorizedError: unauthorized,
    pydantic.ValidationError: validation_error,
    # This special case is used by Starlette for the ServerErrorMiddleware, which always re-raises the error.
    # This generic handler allows us to define our own Internal Server Error response.
    Exception: internal_server_error,
}
