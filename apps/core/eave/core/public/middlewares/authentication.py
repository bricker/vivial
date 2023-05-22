import re
import uuid

import eave.stdlib
import eave.core.internal
import eave.core.public
import sqlalchemy.exc
from asgiref.typing import ASGIReceiveCallable, ASGISendCallable, HTTPScope, Scope

from eave.stdlib.request_state import EaveRequestState
from . import development_bypass
from eave.stdlib.middleware.base import EaveASGIMiddleware
from eave.stdlib.exceptions import BadRequestError


class AuthASGIMiddleware(EaveASGIMiddleware):
    async def __call__(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        if scope["type"] == "http":
            with self.auto_eave_state(scope=scope) as eave_state:
                if development_bypass.development_bypass_allowed(scope=scope):
                    await development_bypass.development_bypass_auth(scope=scope, eave_state=eave_state)
                else:
                    await self._verify_auth(scope=scope, eave_state=eave_state)

        await self.app(scope, receive, send)

    @staticmethod
    async def _verify_auth(scope: HTTPScope, eave_state: EaveRequestState) -> None:
        account_id_header = eave.stdlib.api_util.get_header_value(
            scope=scope, name=eave.stdlib.headers.EAVE_ACCOUNT_ID_HEADER
        )
        if not account_id_header:
            raise eave.stdlib.exceptions.MissingRequiredHeaderError(eave.stdlib.headers.EAVE_ACCOUNT_ID_HEADER)

        account_id = uuid.UUID(account_id_header)

        auth_header = eave.stdlib.api_util.get_header_value(scope=scope, name=eave.stdlib.headers.AUTHORIZATION_HEADER)
        if not auth_header:
            raise eave.stdlib.exceptions.MissingRequiredHeaderError(eave.stdlib.headers.AUTHORIZATION_HEADER)

        auth_header_match = re.match("^Bearer (.+)$", auth_header)
        if auth_header_match is None:
            raise BadRequestError("malformed authorization header")

        access_token: str = auth_header_match.group(1)

        async with eave.core.internal.database.async_session.begin() as db_session:
            eave_account = await eave.core.internal.orm.AccountOrm.one_or_exception(
                session=db_session,
                id=account_id,
                access_token=access_token,
            )

            try:
                await eave_account.verify_oauth_or_exception(session=db_session, log_context=eave_state.log_context)
            except eave.stdlib.exceptions.AccessTokenExpiredError:
                await eave_account.refresh_oauth_token(session=db_session, log_context=eave_state.log_context)
                await eave_account.verify_oauth_or_exception(session=db_session, log_context=eave_state.log_context)

        eave_state.eave_account_id = str(eave_account.id)
        eave_state.eave_team_id = str(eave_account.team_id)
