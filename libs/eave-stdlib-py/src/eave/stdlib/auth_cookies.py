import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from http.cookies import Morsel, SimpleCookie

from eave.stdlib.cookies import (
    EAVE_ACCESS_TOKEN_COOKIE_NAME,
    EAVE_ACCOUNT_ID_COOKIE_NAME,
    EAVE_AUTH_COOKIE_PREFIX,
    EAVE_EMBED_COOKIE_PREFIX,
    delete_cookies_with_prefix,
    set_http_cookie,
)
from eave.stdlib.typing import HTTPFrameworkRequest, HTTPFrameworkResponse


@dataclass
class AuthCookies:
    account_id: str | None
    access_token: str | None

    @property
    def all_set(self) -> bool:
        return bool(self.account_id and self.access_token)


def get_auth_cookies(cookies: SimpleCookie | Mapping[str, str]) -> AuthCookies:
    account_id = cookies.get(EAVE_ACCOUNT_ID_COOKIE_NAME)
    access_token = cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME)

    account_id_decoded = account_id.value if isinstance(account_id, Morsel) else account_id
    access_token_decoded = access_token.value if isinstance(access_token, Morsel) else access_token

    return AuthCookies(
        account_id=account_id_decoded,
        access_token=access_token_decoded,
    )


def set_auth_cookies(
    response: HTTPFrameworkResponse,
    account_id: uuid.UUID | str | None = None,
    access_token: str | None = None,
) -> None:
    if account_id:
        set_http_cookie(
            response=response,
            key=EAVE_ACCOUNT_ID_COOKIE_NAME,
            value=str(account_id),
            secure=True,
            httponly=True,
            samesite="none" # required for CORS-enabled cookies
        )

    if access_token:
        set_http_cookie(
            response=response,
            key=EAVE_ACCESS_TOKEN_COOKIE_NAME,
            value=access_token,
            secure=True,
            httponly=True,
            samesite="none", # required for CORS-enabled cookies
        )


def delete_auth_cookies(request: HTTPFrameworkRequest, response: HTTPFrameworkResponse) -> None:
    delete_cookies_with_prefix(
        request=request,
        response=response,
        prefix=EAVE_AUTH_COOKIE_PREFIX,
        samesite="none", # required for CORS-enabled cookies
    )
    delete_cookies_with_prefix(
        request=request,
        response=response,
        prefix=EAVE_EMBED_COOKIE_PREFIX,
    )
