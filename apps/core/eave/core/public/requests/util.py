import json
import logging
import uuid
from http import HTTPStatus
from typing import Any, Dict, Optional, cast

import eave.core.internal.database as eave_db
import eave.core.internal.orm.account
import eave.stdlib.auth_cookies as eave_auth_cookies
import eave.stdlib.eave_origins as eave_origins
import eave.stdlib.exceptions as eave_errors
import eave.stdlib.headers as eave_headers
import eave.stdlib.util as eave_util
import fastapi
import slack_sdk.errors
import sqlalchemy.exc
from eave.core.internal.orm.account import AccountOrm
from eave.core.internal.orm.auth_token import AuthTokenOrm
from eave.core.internal.orm.team import TeamOrm
from eave.stdlib import logger

from ..middlewares import asgi_types


def not_found(request: fastapi.Request, exc: Exception) -> fastapi.Response:
    eave_state = get_eave_state(request=request)
    logging.error("not found", exc_info=exc, extra=eave_state.log_context)
    return fastapi.responses.Response(
        status_code=HTTPStatus.NOT_FOUND,
        content=eave_state.log_context,
    )


def internal_server_error(request: fastapi.Request, exc: Exception) -> fastapi.Response:
    eave_state = get_eave_state(request=request)
    logging.error("internal server error", exc_info=exc, extra=eave_state.log_context)
    return fastapi.responses.Response(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content=eave_state.log_context,
    )


def bad_request(request: fastapi.Request, exc: Exception) -> fastapi.Response:
    eave_state = get_eave_state(request=request)
    logging.error("bad request", exc_info=exc, extra=eave_state.log_context)
    return fastapi.responses.Response(
        status_code=HTTPStatus.BAD_REQUEST,
        content=eave_state.log_context,
    )


def unauthorized(request: fastapi.Request, exc: Exception) -> fastapi.Response:
    eave_state = get_eave_state(request=request)
    logging.error("unauthorized", exc_info=exc, extra=eave_state.log_context)
    return fastapi.responses.Response(
        status_code=HTTPStatus.UNAUTHORIZED,
        content=eave_state.log_context,
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
    eave_team: TeamOrm
    request_id: uuid.UUID
    request_method: str
    request_scheme: str
    request_path: str

    @property
    def log_context(self) -> Dict[str, str]:
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


async def get_logged_in_account_if_present(request: fastapi.Request, response: fastapi.Response) -> AccountOrm | None:
    eave_access_token = request.cookies.get(eave_headers.EAVE_ACCESS_TOKEN_COOKIE)
    if not eave_access_token:
        return None

    eave_state = get_eave_state(request=request)

    # User might already be logged in. Check the access token.
    # TODO: If the user is logged in through another service provider (eg Google), this won't link Slack to their individual account.

    try:
        async with eave_db.async_session.begin() as db_session:
            tokens = await AuthTokenOrm.find_and_verify_or_exception(
                session=db_session,
                log_context=eave_state.log_context,
                aud=eave_origins.EaveOrigin.eave_www.value,
                access_token=eave_access_token,
                allow_expired=True,  # FIXME: This is only here in case the token expires during the Slack OAuth flow.
            )

        # Now, we've verified that the user previously logged in, but in this case, we don't care how.
        # So, we won't update their account to set the auth_provider, auth_id, or oauth_token.
        # This case occurs when the user logs in separately, and is now connecting their Eave account to their third-party workspace (eg Slack)
        return tokens.account

    except sqlalchemy.exc.SQLAlchemyError as e:
        logger.error("invalid auth token in cookies; clearing cookie", exc_info=e, extra=eave_state.log_context)
        # TODO: Redirect to dashboard instead of throwing an error.
        eave_auth_cookies.delete_auth_cookies(response=response)
        raise eave_errors.InvalidAuthError() from e
