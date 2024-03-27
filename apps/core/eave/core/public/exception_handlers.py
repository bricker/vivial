import http
from typing import Any, Callable, Mapping

import pydantic
from starlette.requests import Request
from starlette.responses import Response

import eave.stdlib.api_util
import eave.stdlib.cookies
from eave.stdlib.auth_cookies import delete_auth_cookies
from eave.stdlib.core_api.models.error import ErrorResponse
from eave.stdlib.exceptions import BadRequestError, ForbiddenError, NotFoundError, UnauthorizedError
from eave.stdlib.logging import eaveLogger
from eave.stdlib.request_state import EaveRequestState


def internal_server_error(request: Request, exc: Exception) -> Response:
    eave_state = EaveRequestState.load(request=request)
    eaveLogger.error(exc, eave_state.ctx)

    model = ErrorResponse(
        status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
        error_message=http.HTTPStatus.INTERNAL_SERVER_ERROR.phrase,
        context=eave_state.ctx.public,
    )

    return eave.stdlib.api_util.json_response(model=model, status_code=model.status_code)


def not_found(request: Request, exc: Exception) -> Response:
    eave_state = EaveRequestState.load(request=request)
    eaveLogger.warning(exc, eave_state.ctx)

    model = ErrorResponse(
        status_code=http.HTTPStatus.NOT_FOUND,
        error_message=http.HTTPStatus.NOT_FOUND.phrase,
        context=eave_state.ctx.public,
    )

    return eave.stdlib.api_util.json_response(model=model, status_code=model.status_code)


def bad_request(request: Request, exc: Exception) -> Response:
    eave_state = EaveRequestState.load(request=request)
    eaveLogger.warning(exc, eave_state.ctx)

    model = ErrorResponse(
        status_code=http.HTTPStatus.BAD_REQUEST,
        error_message=http.HTTPStatus.BAD_REQUEST.phrase,
        context=eave_state.ctx.public,
    )

    return eave.stdlib.api_util.json_response(model=model, status_code=model.status_code)


def unauthorized(request: Request, exc: Exception) -> Response:
    eave_state = EaveRequestState.load(request=request)
    eaveLogger.warning(exc, eave_state.ctx)

    model = ErrorResponse(
        status_code=http.HTTPStatus.UNAUTHORIZED,
        error_message=http.HTTPStatus.UNAUTHORIZED.phrase,
        context=eave_state.ctx.public,
    )
    response = eave.stdlib.api_util.json_response(model=model, status_code=model.status_code)
    delete_auth_cookies(response=response)
    return response


def forbidden(request: Request, exc: Exception) -> Response:
    eave_state = EaveRequestState.load(request=request)
    eaveLogger.warning(exc, eave_state.ctx)

    model = ErrorResponse(
        status_code=http.HTTPStatus.FORBIDDEN,
        error_message=http.HTTPStatus.FORBIDDEN.phrase,
        context=eave_state.ctx.public,
    )
    response = eave.stdlib.api_util.json_response(model=model, status_code=model.status_code)
    return response


def validation_error(request: Request, exc: Exception) -> Response:
    eave_state = EaveRequestState.load(request=request)
    eaveLogger.warning(exc, eave_state.ctx)

    if isinstance(exc, pydantic.ValidationError):
        eave_state.ctx.public["validation_errors"] = exc.json()

    model = ErrorResponse(
        status_code=http.HTTPStatus.UNPROCESSABLE_ENTITY,
        error_message="validation errors",
        context=eave_state.ctx.public,
    )

    return eave.stdlib.api_util.json_response(model=model, status_code=model.status_code)


exception_handlers: Mapping[Any, Callable[[Request, Exception], Response]] = {
    NotFoundError: not_found,
    BadRequestError: bad_request,
    UnauthorizedError: unauthorized,
    ForbiddenError: forbidden,
    # All data validation errors
    pydantic.ValidationError: validation_error,
    # This special case is used by Starlette for the ServerErrorMiddleware, which always re-raises the error.
    # This generic handler allows us to define our own Internal Server Error response.
    Exception: internal_server_error,
}
