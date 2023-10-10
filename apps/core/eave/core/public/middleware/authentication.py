from typing import cast
import uuid
from starlette.datastructures import MutableHeaders

from starlette.responses import Response
from starlette.types import Message
from eave.core.internal.orm.account import AccountOrm
from eave.stdlib.auth_cookies import delete_auth_cookies, set_auth_cookies
from eave.stdlib.core_api.operations import EndpointConfiguration

import eave.stdlib.headers
import eave.stdlib.api_util
import eave.stdlib.exceptions
import eave.core.internal
import eave.core.public
from asgiref.typing import ASGI3Application, ASGIReceiveCallable, ASGISendCallable, ASGISendEvent, HTTPScope, Scope
from eave.stdlib.api_util import get_bearer_token

from eave.stdlib.request_state import EaveRequestState
from eave.stdlib.middleware.development_bypass import development_bypass_allowed
from eave.stdlib.util import ensure_uuid
from .development_bypass import development_bypass_auth
from eave.stdlib.middleware.base import EaveASGIMiddleware
from eave.stdlib.exceptions import UnauthorizedError


class AuthASGIMiddleware(EaveASGIMiddleware):
    endpoint_config: EndpointConfiguration

    def __init__(self, app: ASGI3Application, endpoint_config: EndpointConfiguration) -> None:
        super().__init__(app)
        self.endpoint_config = endpoint_config

    async def __call__(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        if development_bypass_allowed(scope=scope):
            await development_bypass_auth(scope=scope)
            await self.app(scope, receive, send)
            return

        await self._verify_auth(scope=scope)

        await self.app(scope, receive, send)

    async def _verify_auth(self, scope: HTTPScope) -> None:
        eave_state = EaveRequestState.load(scope=scope)

        account_id_header = eave.stdlib.api_util.get_header_value(
            scope=scope, name=eave.stdlib.headers.EAVE_ACCOUNT_ID_HEADER
        )

        access_token = get_bearer_token(scope=scope)

        if account_id_header is None or access_token is None:
            if not self.endpoint_config.auth_required:
                return
            else:
                raise UnauthorizedError("missing required headers")

        async with eave.core.internal.database.async_session.begin() as db_session:
            eave_account = await AccountOrm.one_or_none(
                session=db_session,
                params=AccountOrm.QueryParams(
                    id=ensure_uuid(account_id_header),
                    access_token=access_token,
                )
            )

            if not eave_account:
                raise UnauthorizedError("invalid auth")

            try:
                await eave_account.verify_oauth_or_exception(session=db_session, ctx=eave_state.ctx)
            except eave.stdlib.exceptions.AccessTokenExpiredError:
                await eave_account.refresh_oauth_token(session=db_session, ctx=eave_state.ctx)
                await eave_account.verify_oauth_or_exception(session=db_session, ctx=eave_state.ctx)

        eave_state.ctx.eave_account_id = str(eave_account.id)
        eave_state.ctx.eave_team_id = str(eave_account.team_id)
