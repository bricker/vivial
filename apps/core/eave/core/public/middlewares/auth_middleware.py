from http import HTTPStatus
import re
from typing import Any, Awaitable, Callable, List, Set
import uuid
import fastapi
from . import EaveMiddleware
import eave.core.public.requests.util as request_util
import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
import eave.stdlib.signing as eave_signing
import eave.stdlib.eave_origins as eave_origins
import eave.stdlib.jwt as eave_jwt
import eave.core.public.requests.state as eave_state
import eave.stdlib.core_api.headers as eave_headers
import eave.stdlib.util as eave_util
from eave.stdlib import logger
from eave.core import EAVE_API_SIGNING_KEY, EAVE_API_JWT_ISSUER

_BYPASS: Set[str] = set()

def add_bypass(path: str) -> None:
    global _BYPASS
    _BYPASS.add(path)

class AuthMiddleware(EaveMiddleware):
    async def dispatch(self, request: fastapi.Request, call_next: Callable[[fastapi.Request], Awaitable[fastapi.Response]]) -> fastapi.Response:
        global _BYPASS
        if request.url.path not in _BYPASS:
            # For refresh requests, we still want to do _most_ validations, except the expiry checks.
            expired_ok = request.url.path == "/auth/token/refresh"

            state = eave_state.EaveRequestState(request.state)
            assert state.eave_origin

            auth_header = request.headers.get(eave_headers.EAVE_AUTHORIZATION_HEADER)
            if not auth_header:
                logger.error("auth header missing/empty", extra=request_util.log_context(request))
                raise fastapi.HTTPException(HTTPStatus.UNAUTHORIZED)

            auth_header_match = re.match("^bearer (.+)$", auth_header, re.IGNORECASE)
            if auth_header_match is None:
                logger.error("auth header malformed", extra=request_util.log_context(request))
                raise fastapi.HTTPException(HTTPStatus.UNAUTHORIZED)

            auth_token: str = auth_header_match.group(1)

            async with eave_db.get_async_session() as db_session:
                auth_token_orm = await eave_orm.AuthTokenOrm.one_or_exception(
                    session=db_session,
                    access_token_hashed=eave_util.sha256digest(auth_token),
                )
                if (not expired_ok and auth_token_orm.expired) or auth_token_orm.invalidated is not None:
                    logger.error("auth token expired or invalidated", extra=request_util.log_context(request))
                    raise fastapi.HTTPException(HTTPStatus.UNAUTHORIZED)

                account = await eave_orm.AccountOrm.one_or_exception(
                    session=db_session,
                    id=auth_token_orm.account_id,
                )

                eave_jwt.validate_jwt_or_exception(
                    jwt_encoded=auth_token,
                    signing_key=EAVE_API_SIGNING_KEY,
                    expected_issuer=EAVE_API_JWT_ISSUER,
                    expected_audience=state.eave_origin.value,
                    expected_subject=str(account.id),
                    expected_jti=auth_token_orm.jti,
                    expected_expiry=auth_token_orm.expires,
                    expired_ok=expired_ok,
                )

            request.state.eave_account = account

        response = await call_next(request)
        return response
