from http import HTTPStatus
from typing import cast

import asgiref.typing
import starlette.types
from starlette.datastructures import MutableHeaders
from starlette.requests import Request
from starlette.responses import Response

import eave.core.internal
import eave.core.public
import eave.stdlib.api_util
import eave.stdlib.exceptions
import eave.stdlib.headers
from eave.core.internal.orm.account import AccountOrm
from eave.stdlib.api_util import get_bearer_token
from eave.stdlib.auth_cookies import delete_auth_cookies, get_auth_cookies, set_auth_cookies
from eave.stdlib.core_api.operations import EndpointConfiguration
from eave.stdlib.exceptions import UnauthorizedError
from eave.stdlib.logging import LogContext, eaveLogger
from eave.stdlib.middleware.base import EaveASGIMiddleware
from eave.stdlib.request_state import EaveRequestState
from eave.stdlib.util import ensure_uuid


class AuthASGIMiddleware(EaveASGIMiddleware):
    endpoint_config: EndpointConfiguration

    def __init__(self, app: starlette.types.ASGIApp, endpoint_config: EndpointConfiguration) -> None:
        super().__init__(app)
        self.endpoint_config = endpoint_config

    async def run(
        self,
        scope: asgiref.typing.Scope,
        receive: asgiref.typing.ASGIReceiveCallable,
        send: asgiref.typing.ASGISendCallable,
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        eave_state = EaveRequestState.load(scope=scope)
        request = Request(scope=cast(starlette.types.Scope, scope))

        # Auth can come from either:
        # 1. Headers: Authorization, eave-account-id
        # 2. Cookies: ev_access_token, ev_account_id
        # Any mix is acceptable. Headers take precedence over Cookies.
        auth_cookies = get_auth_cookies(cookies=request.cookies)

        account_id = eave.stdlib.api_util.get_header_value(scope=scope, name=eave.stdlib.headers.EAVE_ACCOUNT_ID_HEADER)

        if account_id is None:
            account_id = auth_cookies.account_id

        access_token = get_bearer_token(scope=scope)

        if access_token is None:
            access_token = auth_cookies.access_token

        try:
            if account_id is None or access_token is None:
                if not self.endpoint_config.auth_required:
                    await self.app(scope, receive, send)
                    return
                else:
                    raise UnauthorizedError("missing auth")

            account = await self._verify_auth(
                account_id_header=account_id, access_token=access_token, ctx=eave_state.ctx
            )
            eave_state.ctx.eave_account_id = str(account.id)
            eave_state.ctx.eave_team_id = str(account.team_id)

        except UnauthorizedError as e:
            eaveLogger.exception(e, eave_state.ctx)
            await self._abort_unauthorized(scope, receive, send)
            return

        async def _send(event: asgiref.typing.ASGISendEvent) -> None:
            if event["type"] != "http.response.start":
                await send(event)
                return

            headers = MutableHeaders(raw=list(event["headers"]))
            response = Response(headers=headers)

            # Set the access_token response cookie in case the access token was refreshed.
            # If the request came from a browser, the cookie will be automatically updated and the user session will continue.
            # If the request came from a server, it is the client's responsibility to get and save the refreshed token from the response cookie.
            set_auth_cookies(
                response=response,
                access_token=account.access_token,
            )

            event["headers"] = response.headers.raw
            await send(event)

        await self.app(scope, receive, _send)

    async def _verify_auth(self, account_id_header: str, access_token: str, ctx: LogContext) -> AccountOrm:
        async with eave.core.internal.database.async_session.begin() as db_session:
            eave_account = await AccountOrm.one_or_none(
                session=db_session,
                params=AccountOrm.QueryParams(
                    id=ensure_uuid(account_id_header),
                    access_token=access_token,
                ),
            )

            if not eave_account:
                raise UnauthorizedError("invalid auth")

            try:
                await eave_account.verify_oauth_or_exception(session=db_session, ctx=ctx)
            except eave.stdlib.exceptions.AccessTokenExpiredError:
                await eave_account.refresh_oauth_token(session=db_session, ctx=ctx)
                await eave_account.verify_oauth_or_exception(session=db_session, ctx=ctx)

        return eave_account

    async def _abort_unauthorized(
        self,
        scope: asgiref.typing.Scope,
        receive: asgiref.typing.ASGIReceiveCallable,
        send: asgiref.typing.ASGISendCallable,
    ) -> None:
        response = Response(status_code=HTTPStatus.UNAUTHORIZED)
        delete_auth_cookies(response=response)
        await response(
            cast(starlette.types.Scope, scope), cast(starlette.types.Receive, receive), cast(starlette.types.Send, send)
        )
