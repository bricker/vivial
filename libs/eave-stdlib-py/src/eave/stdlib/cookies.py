from datetime import datetime
from typing import Literal

from .config import SHARED_CONFIG
from .time import ONE_YEAR_IN_MS
from .typing import HTTPFrameworkRequest, HTTPFrameworkResponse

EAVE_COOKIE_PREFIX = "eavedash."
EAVE_AUTH_COOKIE_PREFIX = f"{EAVE_COOKIE_PREFIX}auth."
EAVE_OAUTH_COOKIE_PREFIX = f"{EAVE_COOKIE_PREFIX}oauth."
EAVE_EMBED_COOKIE_PREFIX = f"{EAVE_COOKIE_PREFIX}embed."

EAVE_ACCOUNT_ID_COOKIE_NAME = f"{EAVE_AUTH_COOKIE_PREFIX}account_id"
EAVE_ACCESS_TOKEN_COOKIE_NAME = f"{EAVE_AUTH_COOKIE_PREFIX}access_token"

EAVE_OAUTH_STATE_COOKIE_PREFIX = f"{EAVE_OAUTH_COOKIE_PREFIX}state_"


def get_cookies_with_prefix(request: HTTPFrameworkRequest, prefix: str) -> dict[str, str]:
    cookies: dict[str, str] = {}
    for name, value in request.cookies.items():
        if name.startswith(prefix):
            cookies[name] = value

    return cookies


def delete_cookies_with_prefix(
    request: HTTPFrameworkRequest,
    response: HTTPFrameworkResponse,
    prefix: str,
    path: str | None = None,
    domain: str | None = None,
    httponly: bool | None = None,
    samesite: Literal["lax", "strict", "none"] | None = None,
) -> None:
    for name, _ in get_cookies_with_prefix(request=request, prefix=prefix).items():
        delete_http_cookie(
            response=response,
            key=name,
            domain=domain,
            httponly=httponly,
            path=path,
            samesite=samesite,
        )


def set_http_cookie(
    *,
    response: HTTPFrameworkResponse,
    key: str,
    value: str,
    max_age: int | None = None,
    expires: datetime | int | str | None = None,
    path: str = "/",
    domain: str | None = None,
    httponly: bool = True,
    samesite: Literal["lax", "strict", "none"] | None = "lax",
) -> None:
    response.set_cookie(
        key=key,
        value=value,
        max_age=max_age if max_age is not None else int(ONE_YEAR_IN_MS / 1000),
        expires=expires,
        path=path,
        domain=domain if domain is not None else SHARED_CONFIG.eave_cookie_domain,
        secure=(not SHARED_CONFIG.is_development),
        httponly=httponly,
        samesite=samesite,
    )


def delete_http_cookie(
    *,
    response: HTTPFrameworkResponse,
    key: str,
    path: str | None = None,
    domain: str | None = None,
    httponly: bool | None = None,
    samesite: Literal["lax", "strict", "none"] | None = None,
) -> None:
    response.delete_cookie(
        key=key,
        path=path if path is not None else "/",
        domain=domain if domain is not None else SHARED_CONFIG.eave_cookie_domain,
        secure=(not SHARED_CONFIG.is_development),
        httponly=httponly if httponly is not None else True,
        samesite=samesite if samesite is not None else "lax",
    )
