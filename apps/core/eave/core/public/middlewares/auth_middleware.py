import re
import uuid
from typing import Set

import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
import eave.core.public.requests.util as request_util
import eave.stdlib.core_api.headers as eave_headers
import eave.stdlib.exceptions as eave_exceptions
import eave.stdlib.jwt as eave_jwt
import eave.stdlib.util as eave_util
import sqlalchemy.exc
from eave.core import EAVE_API_JWT_ISSUER, EAVE_API_SIGNING_KEY
from eave.stdlib import logger

from . import EaveASGIMiddleware, asgi_types

_BYPASS: Set[str] = set()


def add_bypass(path: str) -> None:
    global _BYPASS
    _BYPASS.add(path)


class AuthASGIMiddleware(EaveASGIMiddleware):
    async def __call__(
        self, scope: asgi_types.Scope, receive: asgi_types.ASGIReceiveCallable, send: asgi_types.ASGISendCallable
    ) -> None:
        if scope["type"] == "http" and scope["path"] not in _BYPASS:
            if EaveASGIMiddleware.development_bypass_allowed(scope=scope):
                logger.warning("Bypassing auth verification in dev environment")
                await self._development_bypass(scope=scope)
            else:
                await self._verify_auth(scope=scope)

        await self.app(scope, receive, send)

    @staticmethod
    async def _verify_auth(scope: asgi_types.HTTPScope) -> None:
        eave_state = request_util.get_eave_state(scope=scope)

        # For refresh requests, we still want to do _most_ validations, except the expiry checks.
        expired_ok = scope["path"] == "/auth/token/refresh"

        auth_header = request_util.get_header_value(scope=scope, name=eave_headers.EAVE_AUTHORIZATION_HEADER)
        if not auth_header:
            logger.error("auth header missing/empty", extra=request_util.log_context(scope=scope))
            raise eave_exceptions.InvalidAuthError()

        auth_header_match = re.match("^Bearer (.+)$", auth_header)
        if auth_header_match is None:
            logger.error("auth header malformed", extra=request_util.log_context(scope=scope))
            raise eave_exceptions.InvalidAuthError()

        auth_token: str = auth_header_match.group(1)

        async with eave_db.get_async_session() as db_session:
            try:
                auth_token_orm = await eave_orm.AuthTokenOrm.one_or_exception(
                    session=db_session,
                    access_token_hashed=eave_util.sha256hexdigest(auth_token),
                )
                if (auth_token_orm.expired and not expired_ok) or (auth_token_orm.invalidated is not None):
                    logger.error("auth token expired or invalidated", extra=request_util.log_context(scope=scope))
                    raise eave_exceptions.AccessTokenExpiredError()

                account = await eave_orm.AccountOrm.one_or_exception(
                    session=db_session,
                    id=auth_token_orm.account_id,
                )
            except sqlalchemy.exc.SQLAlchemyError as e:
                logger.error("auth token or account not found", extra=request_util.log_context(scope=scope))
                raise eave_exceptions.UnauthorizedError()

        eave_jwt.validate_jwt_or_exception(
            jwt_encoded=auth_token,
            signing_key=EAVE_API_SIGNING_KEY,
            expected_issuer=EAVE_API_JWT_ISSUER,
            expected_audience=eave_state.eave_origin.value,
            expected_subject=str(account.id),
            expected_jti=auth_token_orm.jti,
            expected_expiry=auth_token_orm.expires,
            expired_ok=expired_ok,
        )

        eave_state.eave_account = account

    async def _development_bypass(self, scope: asgi_types.HTTPScope) -> None:
        eave_state = request_util.get_eave_state(scope=scope)
        account_id = request_util.get_header_value(scope=scope, name=eave_headers.EAVE_AUTHORIZATION_HEADER)
        if not account_id:
            raise Exception()

        async with eave_db.get_async_session() as db_session:
            account = await eave_orm.AccountOrm.one_or_exception(
                session=db_session,
                id=uuid.UUID(account_id),
            )

        eave_state.eave_account = account
