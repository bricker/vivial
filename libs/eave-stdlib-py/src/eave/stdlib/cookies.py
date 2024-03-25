from .time import ONE_YEAR_IN_MS
from .typing import HTTPFrameworkResponse

from .config import SHARED_CONFIG


def set_http_cookie(
    *,
    response: HTTPFrameworkResponse,
    key: str,
    value: str,
    httponly: bool = True,
) -> None:
    response.set_cookie(
        key=key,
        value=value,
        domain=SHARED_CONFIG.eave_cookie_domain,
        path="/",
        httponly=httponly,
        secure=(not SHARED_CONFIG.is_development),
        samesite="lax",
        max_age=int(ONE_YEAR_IN_MS / 1000),
    )


def delete_http_cookie(
    *,
    response: HTTPFrameworkResponse,
    key: str,
    httponly: bool = True,
) -> None:
    response.delete_cookie(
        key=key,
        domain=SHARED_CONFIG.eave_cookie_domain,
        path="/",
        httponly=httponly,
        secure=(not SHARED_CONFIG.is_development),
        samesite="lax",
    )
