from uuid import UUID, uuid4

from starlette.responses import Response

from eave.core.config import JWT_AUDIENCE, JWT_ISSUER
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.cookies import (
    VIVIAL_COOKIE_PREFIX,
    delete_http_cookie,
    set_http_cookie,
)
from eave.stdlib.jwt import JWTPurpose, create_jws
from eave.stdlib.time import ONE_YEAR_IN_MINUTES, ONE_YEAR_IN_SECONDS

AUTH_COOKIE_PREFIX = f"{VIVIAL_COOKIE_PREFIX}auth."
ACCESS_TOKEN_COOKIE_NAME = f"{AUTH_COOKIE_PREFIX}access_token"
REFRESH_TOKEN_COOKIE_NAME = f"{AUTH_COOKIE_PREFIX}refresh_token"

ACCESS_TOKEN_MAX_AGE_MINUTES = 30


def set_new_auth_cookies(*, response: Response, account_id: UUID) -> None:
    jwt_id = str(uuid4())

    access_token = create_jws(
        purpose=JWTPurpose.ACCESS,
        issuer=JWT_ISSUER,
        audience=JWT_AUDIENCE,
        subject=str(account_id),
        jwt_id=jwt_id,
        max_age_minutes=ACCESS_TOKEN_MAX_AGE_MINUTES,
    )

    refresh_token = create_jws(
        purpose=JWTPurpose.REFRESH,
        issuer=JWT_ISSUER,
        audience=JWT_AUDIENCE,
        subject=str(account_id),
        jwt_id=jwt_id,
        max_age_minutes=ONE_YEAR_IN_MINUTES,
    )

    set_http_cookie(
        response=response,
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        max_age_seconds=ONE_YEAR_IN_SECONDS,
        domain=SHARED_CONFIG.eave_api_hostname_public,
        path="/",
        samesite="lax",
        httponly=True,
        secure=True,
    )

    set_http_cookie(
        response=response,
        key=REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token,
        max_age_seconds=ONE_YEAR_IN_SECONDS,
        domain=SHARED_CONFIG.eave_api_hostname_public,
        path="/public/refresh_tokens",
        samesite="lax",
        httponly=True,
        secure=True,
    )


def delete_auth_cookies(*, response: Response) -> None:
    delete_http_cookie(
        response=response,
        key=ACCESS_TOKEN_COOKIE_NAME,
        domain=SHARED_CONFIG.eave_api_hostname_public,
        path="/",
        samesite="lax",
        httponly=True,
        secure=True,
    )

    delete_http_cookie(
        response=response,
        key=REFRESH_TOKEN_COOKIE_NAME,
        domain=SHARED_CONFIG.eave_api_hostname_public,
        path="/public/refresh_tokens",
        samesite="lax",
        httponly=True,
        secure=True,
    )
