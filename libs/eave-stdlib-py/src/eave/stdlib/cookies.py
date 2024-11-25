from datetime import datetime
from typing import Literal

from .config import SHARED_CONFIG
from .typing import HTTPFrameworkResponse

EAVE_COOKIE_PREFIX = "eavedash."
EAVE_AUTH_COOKIE_PREFIX = f"{EAVE_COOKIE_PREFIX}auth."

EAVE_ACCESS_TOKEN_COOKIE_NAME = f"{EAVE_AUTH_COOKIE_PREFIX}access_token"
EAVE_REFRESH_TOKEN_COOKIE_NAME = f"{EAVE_AUTH_COOKIE_PREFIX}refresh_token"


def set_http_cookie(
    *,
    response: HTTPFrameworkResponse,
    key: str,
    value: str,
    max_age_seconds: int | None = None,
    expires: datetime | int | str | None = None,
    path: str = "/",
    domain: str | None = None,
    secure: bool = True,
    httponly: bool = True,
    samesite: Literal["lax", "strict", "none"] = "lax",
) -> None:
    response.set_cookie(
        key=key,
        value=value,
        max_age=max_age_seconds,
        expires=expires,
        path=path,
        domain=domain if domain is not None else SHARED_CONFIG.eave_hostname_public,
        secure=secure,
        httponly=httponly,
        samesite=samesite,
    )


def delete_http_cookie(
    *,
    response: HTTPFrameworkResponse,
    key: str,
    path: str = "/",
    domain: str | None = None,
    secure: bool = True,
    httponly: bool = True,
    samesite: Literal["lax", "strict", "none"] = "lax",
) -> None:
    response.delete_cookie(
        key=key,
        path=path,
        domain=domain if domain is not None else SHARED_CONFIG.eave_hostname_public,
        secure=secure,
        httponly=httponly,
        samesite=samesite,
    )
