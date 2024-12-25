from http import HTTPStatus
from typing import override
from uuid import UUID

from asgiref.typing import HTTPScope
from sqlalchemy.exc import NoResultFound
from starlette.requests import Request
from starlette.responses import Response

from eave.core import database
from eave.core.auth_cookies import (
    ACCESS_TOKEN_COOKIE_NAME,
    REFRESH_TOKEN_COOKIE_NAME,
    delete_auth_cookies,
    set_new_auth_cookies,
)
from eave.core.config import JWT_AUDIENCE, JWT_ISSUER
from eave.core.orm.account import AccountOrm
from eave.stdlib.headers import MIME_TYPE_TEXT
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.jwt import InvalidTokenError, JWTPurpose, validate_jws_or_exception, validate_jws_pair_or_exception


class RefreshTokensEndpoint(HTTPEndpoint):
    @override
    async def handle(self, request: Request, scope: HTTPScope) -> Response:
        encoded_access_token = request.cookies.get(ACCESS_TOKEN_COOKIE_NAME)
        encoded_refresh_token = request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)

        response = Response(media_type=MIME_TYPE_TEXT)

        try:
            if not encoded_access_token or not encoded_refresh_token:
                raise InvalidTokenError("missing tokens")

            # This token is assumed to be expired, so when validating we ignore the expiration date.
            access_jws = validate_jws_or_exception(
                encoded_jws=encoded_access_token,
                expected_issuer=JWT_ISSUER,
                expected_audience=JWT_AUDIENCE,
                expected_purpose=JWTPurpose.ACCESS,
                expired_ok=True,
            )

            refresh_jws = validate_jws_or_exception(
                encoded_jws=encoded_refresh_token,
                expected_issuer=JWT_ISSUER,
                expected_audience=JWT_AUDIENCE,
                expected_purpose=JWTPurpose.REFRESH,
                expired_ok=False,
            )

            validate_jws_pair_or_exception(access_token=access_jws, refresh_token=refresh_jws)

            async with database.async_session.begin() as db_session:
                account_orm = await AccountOrm.get_one(db_session, UUID(refresh_jws.payload.sub))

            set_new_auth_cookies(response=response, account_id=account_orm.id)
            response.status_code = HTTPStatus.OK
            return response

        except (InvalidTokenError, NoResultFound):
            delete_auth_cookies(response=response)
            response.status_code = HTTPStatus.UNAUTHORIZED
            return response
