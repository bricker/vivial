import asyncio
import json
import logging
import typing
import uuid
from http import HTTPStatus
from typing import Any, Dict, Optional, cast

import eave.core.internal.orm.account
import eave.core.internal.orm.team
import eave.stdlib.eave_origins as eave_origins
import eave.stdlib.exceptions as eave_errors
import eave.stdlib.util as eave_util
import fastapi
import slack_sdk.errors
import sqlalchemy.exc
from eave.stdlib import logger

from ..middlewares import asgi_types


def not_found(request: fastapi.Request, exc: Exception) -> fastapi.Response:
    eave_state = get_eave_state(request=request)
    logging.error("not found", exc_info=exc, extra=eave_state.log_context)
    return fastapi.responses.Response(
        status_code=HTTPStatus.NOT_FOUND,
        content=json.dumps(eave_state.log_context),
    )


def internal_server_error(request: fastapi.Request, exc: Exception) -> fastapi.Response:
    eave_state = get_eave_state(request=request)
    logging.error("internal server error", exc_info=exc, extra=eave_state.log_context)
    return fastapi.responses.Response(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content=json.dumps(eave_state.log_context),
    )


def bad_request(request: fastapi.Request, exc: Exception) -> fastapi.Response:
    eave_state = get_eave_state(request=request)
    logging.error("bad request", exc_info=exc, extra=eave_state.log_context)
    return fastapi.responses.Response(
        status_code=HTTPStatus.BAD_REQUEST,
        content=json.dumps(eave_state.log_context),
    )


def unauthorized(request: fastapi.Request, exc: Exception) -> fastapi.Response:
    eave_state = get_eave_state(request=request)
    logging.error("unauthorized", exc_info=exc, extra=eave_state.log_context)
    return fastapi.responses.Response(
        status_code=HTTPStatus.UNAUTHORIZED,
        content=json.dumps(eave_state.log_context),
    )


def validation_error(request: fastapi.Request, exc: fastapi.exceptions.RequestValidationError) -> fastapi.Response:
    eave_state = get_eave_state(request=request)
    logger.error("validation error", exc_info=exc, extra=eave_state.log_context)
    return fastapi.Response(status_code=HTTPStatus.UNPROCESSABLE_ENTITY)


def add_standard_exception_handlers(app: fastapi.FastAPI) -> None:
    app.exception_handler(sqlalchemy.exc.NoResultFound)(not_found)
    app.exception_handler(sqlalchemy.exc.MultipleResultsFound)(internal_server_error)
    app.exception_handler(eave_errors.BadRequestError)(bad_request)
    app.exception_handler(eave_errors.UnauthorizedError)(unauthorized)
    app.exception_handler(eave_errors.InternalServerError)(internal_server_error)
    app.exception_handler(fastapi.exceptions.RequestValidationError)(validation_error)
    app.exception_handler(slack_sdk.errors.SlackApiError)(internal_server_error)


class EaveRequestState:
    eave_account: eave.core.internal.orm.account.AccountOrm
    eave_origin: eave_origins.EaveOrigin
    eave_team: eave.core.internal.orm.team.TeamOrm
    request_id: uuid.UUID
    request_method: str
    request_scheme: str
    request_path: str
    _notes: typing.Optional[typing.List[str]] = None

    @property
    def log_context(self) -> Dict[str, object]:
        context: Dict[str, object] = {}

        if hasattr(self, "eave_account"):
            context["eave_account_id"] = str(self.eave_account.id)
        if hasattr(self, "eave_origin"):
            context["eave_origin"] = self.eave_origin.value
        if hasattr(self, "eave_team"):
            context["eave_team_id"] = str(self.eave_team.id)
        if hasattr(self, "request_id"):
            context["request_id"] = str(self.request_id)
        if hasattr(self, "request_method"):
            context["request_method"] = str(self.request_method)
        if hasattr(self, "request_scheme"):
            context["request_scheme"] = str(self.request_scheme)
        if hasattr(self, "request_path"):
            context["request_path"] = str(self.request_path)
        if hasattr(self, "_notes"):
            # Probably not thread-safe
            context["notes"] = self._notes

        return context

    @property
    def public_error_response_body(self) -> str:
        """
        Return this from an endpoint to give the caller some context.
        """

        context: Dict[str, str] = {}

        if hasattr(self, "eave_account"):
            context["eave_account_id"] = str(self.eave_account.id)
        if hasattr(self, "eave_origin"):
            context["eave_origin"] = self.eave_origin.value
        if hasattr(self, "eave_team"):
            context["eave_team_id"] = str(self.eave_team.id)
        if hasattr(self, "request_id"):
            context["request_id"] = str(self.request_id)
        if hasattr(self, "request_method"):
            context["request_method"] = str(self.request_method)
        if hasattr(self, "request_scheme"):
            context["request_scheme"] = str(self.request_scheme)
        if hasattr(self, "request_path"):
            context["request_path"] = str(self.request_path)

        return json.dumps(context)

    _semaphore = asyncio.Semaphore()

    async def add_note(self, note: str) -> None:
        async with self._semaphore:
            if self._notes is None:
                self._notes = []

            self._notes.append(note)


def get_eave_state(
    scope: Optional[asgi_types.Scope] = None, request: Optional[fastapi.Request] = None
) -> EaveRequestState:
    # Validate that exactly one parameter is supplied.
    assert eave_util.xor(scope, request)

    if scope is None and request is not None:
        scope = cast(asgi_types.Scope, request.scope)

    assert scope is not None
    scope.setdefault("state", dict[str, Any]())
    state = scope.get("state")
    assert state is not None  # Helps the typechecker

    eave_state = state.get("eave")
    if eave_state is None:
        eave_state = EaveRequestState()
        state["eave"] = eave_state

    if scope["type"] == "http":
        eave_state.request_method = scope["method"]
        eave_state.request_scheme = scope["scheme"]
        eave_state.request_path = scope["path"]

    return cast(EaveRequestState, eave_state)


def get_header_value(scope: asgi_types.HTTPScope, name: str) -> str | None:
    """
    This function doesn't support multiple headers with the same name.
    It will always choose the "first" one (from whatever order the ASGI server sent).
    See here for details about the scope["headers"] object:
    https://asgi.readthedocs.io/en/latest/specs/www.html#http-connection-scope
    """
    return next((v.decode() for [n, v] in scope["headers"] if n.decode().lower() == name.lower()), None)
