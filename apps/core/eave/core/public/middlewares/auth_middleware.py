import re
from typing import Set

import eave.core.internal.database as eave_db
import eave.core.public.requests.util as request_util
import eave.stdlib.exceptions as eave_exceptions
import eave.stdlib.headers as eave_headers
import sqlalchemy.exc
from eave.core.internal.orm.auth_token import AuthTokenOrm
from eave.stdlib import logger

from . import EaveASGIMiddleware, _development_bypass, asgi_types

_ROUTE_BYPASS: Set[str] = set()


def add_bypass(path: str) -> None:
    global _ROUTE_BYPASS
    _ROUTE_BYPASS.add(path)


class AuthASGIMiddleware(EaveASGIMiddleware):
    async def __call__(
        self, scope: asgi_types.Scope, receive: asgi_types.ASGIReceiveCallable, send: asgi_types.ASGISendCallable
    ) -> None:
        if scope["type"] == "http" and scope["path"] not in _ROUTE_BYPASS:
            if _development_bypass.development_bypass_allowed(scope=scope):
                await _development_bypass.development_bypass_auth(scope=scope)
            else:
                await self._verify_auth(scope=scope)

        await self.app(scope, receive, send)

    @staticmethod
    async def _verify_auth(scope: asgi_types.HTTPScope) -> None:
        eave_state = request_util.get_eave_state(scope=scope)

        auth_header = request_util.get_header_value(scope=scope, name=eave_headers.EAVE_AUTHORIZATION_HEADER)
        if not auth_header:
            logger.error("auth header missing/empty", extra=eave_state.log_context)
            raise eave_exceptions.InvalidAuthError()

        auth_header_match = re.match("^Bearer (.+)$", auth_header)
        if auth_header_match is None:
            logger.error("auth header malformed", extra=eave_state.log_context)
            raise eave_exceptions.InvalidAuthError()

        access_token: str = auth_header_match.group(1)

        async with eave_db.async_session.begin() as db_session:
            try:
                token = await AuthTokenOrm.find_and_verify_or_exception(
                    session=db_session,
                    log_context=eave_state.log_context,
                    access_token=access_token,
                    aud=eave_state.eave_origin,
                    allow_expired=False,
                )
            except sqlalchemy.exc.SQLAlchemyError as e:
                logger.error("auth token or account not found", exc_info=e, extra=eave_state.log_context)
                raise eave_exceptions.UnauthorizedError()

        eave_state.eave_account = token.account
