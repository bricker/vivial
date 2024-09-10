from abc import ABC
from collections.abc import Awaitable, Callable
from http import HTTPStatus
from typing import cast

import aiohttp
import asgiref.typing
import starlette.types
from starlette.requests import Request
from starlette.responses import Response

import eave.core.internal
import eave.core.public
import eave.stdlib.api_util
import eave.stdlib.exceptions
import eave.stdlib.headers
from eave.core.internal import database
from eave.core.internal.orm.client_credentials import ClientCredentialsOrm, ClientScope
from eave.core.internal.orm.team import TeamOrm
from eave.stdlib.api_util import get_header_value_or_exception
from eave.stdlib.exceptions import ForbiddenError, UnauthorizedError
from eave.stdlib.logging import LogContext, eaveLogger
from eave.stdlib.middleware.base import EaveASGIMiddleware
from eave.stdlib.util import ensure_uuid


async def _get_creds_from_qp(request: Request, scope: asgiref.typing.HTTPScope) -> ClientCredentialsOrm:
    origin_header = get_header_value_or_exception(scope=scope, name=aiohttp.hdrs.ORIGIN)
    client_id = request.query_params.get("clientId")

    if client_id is None:
        raise UnauthorizedError("missing clientId query param")

    async with database.async_session.begin() as db_session:
        creds = (
            await ClientCredentialsOrm.query(
                session=db_session,
                params=ClientCredentialsOrm.QueryParams(
                    id=ensure_uuid(client_id),
                ),
            )
        ).one_or_none()

        if not creds:
            raise UnauthorizedError("invalid credentials")

        if not (creds.scope & ClientScope.write) > 0:
            raise ForbiddenError("invalid scope")

        eave_team = await TeamOrm.one_or_exception(session=db_session, team_id=creds.team_id)

        # validate source origin is allowed by team settings
        if not eave_team.origin_allowed(origin=origin_header):
            raise ForbiddenError("invalid origin")

        creds.touch(session=db_session)

    return creds


async def _get_creds_from_headers(scope: asgiref.typing.HTTPScope) -> ClientCredentialsOrm:
    client_id = get_header_value_or_exception(scope=scope, name=eave.stdlib.headers.EAVE_CLIENT_ID_HEADER)
    client_secret = get_header_value_or_exception(scope=scope, name=eave.stdlib.headers.EAVE_CLIENT_SECRET_HEADER)

    async with database.async_session.begin() as db_session:
        creds = (
            await ClientCredentialsOrm.query(
                session=db_session,
                params=ClientCredentialsOrm.QueryParams(
                    id=ensure_uuid(client_id),
                    secret=client_secret,
                ),
            )
        ).one_or_none()

        if not creds:
            raise UnauthorizedError("invalid credentials")

        if not (creds.scope & ClientScope.write) > 0:
            raise ForbiddenError("invalid scopes")

        creds.touch(session=db_session)
    return creds


async def _abort(
    request: Request,
    status_code: HTTPStatus,
    scope: asgiref.typing.Scope,
    receive: asgiref.typing.ASGIReceiveCallable,
    send: asgiref.typing.ASGISendCallable,
) -> None:
    response = Response(status_code=status_code)
    await response(
        cast(starlette.types.Scope, scope), cast(starlette.types.Receive, receive), cast(starlette.types.Send, send)
    )


class CredsAuthMiddlewareBase(EaveASGIMiddleware, ABC):
    async def process_request(
        self,
        scope: asgiref.typing.HTTPScope,
        receive: asgiref.typing.ASGIReceiveCallable,
        send: asgiref.typing.ASGISendCallable,
        request: Request,
        ctx: LogContext,
        continue_request: Callable[[], Awaitable[None]],
    ) -> None:
        try:
            creds = await self._get_creds(scope=scope, request=request)

            ctx.eave_authed_team_id = str(creds.team_id)
            ctx.eave_client_id = str(creds.id)
        except UnauthorizedError as e:
            eaveLogger.exception(e, ctx)
            await _abort(request=request, status_code=HTTPStatus.UNAUTHORIZED, scope=scope, receive=receive, send=send)
            return
        except ForbiddenError as e:
            eaveLogger.exception(e, ctx)
            await _abort(request=request, status_code=HTTPStatus.FORBIDDEN, scope=scope, receive=receive, send=send)
            return

        await self.app(scope, receive, send)

    async def _get_creds(self, scope: asgiref.typing.HTTPScope, request: Request) -> ClientCredentialsOrm: ...


class ClientCredentialsFromHeadersASGIMiddleware(CredsAuthMiddlewareBase):
    async def _get_creds(self, scope: asgiref.typing.HTTPScope, request: Request) -> ClientCredentialsOrm:
        return await _get_creds_from_headers(scope)


class ClientCredentialsFromQueryParamsASGIMiddleware(CredsAuthMiddlewareBase):
    async def _get_creds(self, scope: asgiref.typing.HTTPScope, request: Request) -> ClientCredentialsOrm:
        return await _get_creds_from_qp(request=request, scope=scope)


class ClientCredentialsFromHeadersOrQueryParamsASGIMiddleware(CredsAuthMiddlewareBase):
    async def _get_creds(self, scope: asgiref.typing.HTTPScope, request: Request) -> ClientCredentialsOrm:
        creds: ClientCredentialsOrm | None = None
        # validate using clientId qp if one is provided
        client_id = request.query_params.get("clientId")
        if client_id:
            creds = await _get_creds_from_qp(request=request, scope=scope)

        # enforce client auth for non-browser requests
        if not creds:
            creds = await _get_creds_from_headers(scope)
        return creds
