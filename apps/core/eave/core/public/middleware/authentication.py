import uuid

import eave.stdlib.headers
import eave.stdlib.api_util
import eave.stdlib.exceptions
import eave.core.internal
import eave.core.public
from asgiref.typing import ASGIReceiveCallable, ASGISendCallable, HTTPScope, Scope
from eave.stdlib.api_util import get_bearer_token

from eave.stdlib.request_state import EaveRequestState
from eave.stdlib.middleware.development_bypass import development_bypass_allowed
from .development_bypass import development_bypass_auth
from eave.stdlib.middleware.base import EaveASGIMiddleware
from eave.stdlib.exceptions import BadRequestError


class AuthASGIMiddleware(EaveASGIMiddleware):
    async def __call__(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        if scope["type"] == "http":
            if development_bypass_allowed(scope=scope):
                await development_bypass_auth(scope=scope)
            else:
                await self._verify_auth(scope=scope)

        await self.app(scope, receive, send)

    async def _verify_auth(self, scope: HTTPScope) -> None:
        eave_state = EaveRequestState.load(scope=scope)

        account_id_header = eave.stdlib.api_util.get_header_value(
            scope=scope, name=eave.stdlib.headers.EAVE_ACCOUNT_ID_HEADER
        )
        if not account_id_header:
            if not self.endpoint_config.auth_required:
                return
            else:
                raise eave.stdlib.exceptions.MissingRequiredHeaderError(eave.stdlib.headers.EAVE_ACCOUNT_ID_HEADER)

        account_id = uuid.UUID(account_id_header)

        access_token = get_bearer_token(scope=scope)
        if access_token is None:
            raise BadRequestError("malformed or missing authorization header")

        async with eave.core.internal.database.async_session.begin() as db_session:
            eave_account = await eave.core.internal.orm.AccountOrm.one_or_exception(
                session=db_session,
                id=account_id,
                access_token=access_token,
            )

            try:
                await eave_account.verify_oauth_or_exception(session=db_session, ctx=eave_state.ctx)
            except eave.stdlib.exceptions.AccessTokenExpiredError:
                await eave_account.refresh_oauth_token(session=db_session, ctx=eave_state.ctx)
                await eave_account.verify_oauth_or_exception(session=db_session, ctx=eave_state.ctx)

        eave_state.ctx.eave_account_id = str(eave_account.id)
        eave_state.ctx.eave_team_id = str(eave_account.team_id)
