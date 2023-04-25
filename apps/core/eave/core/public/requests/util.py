import logging
from http import HTTPStatus
from http.client import HTTPException
from typing import Any, Optional, cast
from uuid import UUID
import uuid

import eave.stdlib.eave_origins as eave_origins

import eave.core.internal.orm as eave_orm
import eave.stdlib.exceptions as eave_errors
import fastapi
import sqlalchemy.exc
from eave.stdlib import logger
from sqlalchemy.ext.asyncio import AsyncSession
from ..middlewares import asgi_types

def not_found(request: fastapi.Request, exc: Exception) -> fastapi.Response:
    logging.error("not found", exc_info=exc)
    return fastapi.responses.Response(status_code=HTTPStatus.NOT_FOUND)


def internal_server_error(request: fastapi.Request, exc: Exception) -> fastapi.Response:
    logging.error("internal server error", exc_info=exc)
    return fastapi.responses.Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)


def bad_request(request: fastapi.Request, exc: Exception) -> fastapi.Response:
    logging.error("bad request", exc_info=exc)
    return fastapi.responses.Response(status_code=HTTPStatus.BAD_REQUEST)

def unauthorized(request: fastapi.Request, exc: Exception) -> fastapi.Response:
    logging.error("unauthorized", exc_info=exc)
    return fastapi.responses.Response(status_code=HTTPStatus.UNAUTHORIZED)


def validation_error(request: fastapi.Request, exc: fastapi.exceptions.RequestValidationError) -> fastapi.Response:
    logger.error(exc)
    logger.info(exc.body)
    return fastapi.Response(status_code=HTTPStatus.UNPROCESSABLE_ENTITY)


def add_standard_exception_handlers(app: fastapi.FastAPI) -> None:
    app.exception_handler(sqlalchemy.exc.NoResultFound)(not_found)
    app.exception_handler(sqlalchemy.exc.MultipleResultsFound)(internal_server_error)
    app.exception_handler(eave_errors.BadRequestError)(bad_request)
    app.exception_handler(eave_errors.UnauthorizedError)(unauthorized)
    app.exception_handler(eave_errors.InternalServerError)(internal_server_error)
    app.exception_handler(fastapi.exceptions.RequestValidationError)(validation_error)

def log_context(scope: Optional[asgi_types.Scope] = None, request: Optional[fastapi.Request] = None) -> dict[str, Any]:
    """
    This function is overly cautious because it's important that there aren't failures during logging.
    """
    # Validate that exactly one parameter is supplied.
    assert xor(scope, request)
    context: dict[str,Any] = {}

    try:
        if scope is None and request is not None:
            scope = cast(asgi_types.Scope, request.scope)

        if scope is None:
            return context

        state = scope.get("state")
        if state is None:
            return context

        eave_state = state.get("eave")
        if eave_state is None:
            return context

        eave_state = cast(EaveRequestState, eave_state)
        context["request_id"] = eave_state.request_id
    except Exception as e:
        logger.error("Error during logging.", exc_info=e)

    return context

class EaveRequestState:
    eave_account: eave_orm.AccountOrm
    eave_origin: eave_origins.EaveOrigin
    eave_team: eave_orm.TeamOrm
    request_id: uuid.UUID

def get_eave_state(scope: Optional[asgi_types.Scope] = None, request: Optional[fastapi.Request] = None) -> EaveRequestState:
    # Validate that exactly one parameter is supplied.
    assert xor(scope, request)

    if scope is None and request is not None:
        state = request.state
        scope = cast(asgi_types.Scope, request.scope)

    assert scope is not None
    assert scope["state"] is not None

    try:
        existing_state: EaveRequestState = scope["state"]["eave"]
        return existing_state
    except KeyError:
        new_state = EaveRequestState()
        scope["state"]["eave"] = new_state
        return new_state

def get_header_value(scope: asgi_types.HTTPScope, name: str) -> str | None:
    """
    This function doesn't support multiple headers with the same name.
    It will always choose the "first" one (from whatever order the ASGI server sent).
    See here for details about the scope["headers"] object:
    https://asgi.readthedocs.io/en/latest/specs/www.html#http-connection-scope
    """
    return next((
        v.decode()
        for [n, v] in scope["headers"]
        if n.decode().lower() == name.lower()
    ), None)

def xor(a: Any, b: Any) -> bool:
    # The "not"s here are just a quick way to turn the objects into booleans, the actual value doesn't matter for xor
    return (not a) ^ (not b)