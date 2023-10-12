from http.cookies import SimpleCookie
import typing
from datetime import datetime
from typing import Any, Literal, Optional, Protocol

from eave.stdlib.typing import HTTPFrameworkResponse, StarletteResponse, WerkzeugResponse

from .config import shared_config

_ONE_YEAR_SECONDS = (60 * 60 * 24 * 365)

def set_http_cookie(
    response: HTTPFrameworkResponse,
    key: str,
    value: str,
    httponly: bool = True,
) -> None:
    response.set_cookie(
        key=key,
        value=value,
        domain=shared_config.eave_cookie_domain,
        path="/",
        httponly=httponly,
        secure=(not shared_config.is_development),
        samesite="lax",
        max_age=_ONE_YEAR_SECONDS,
    )

def delete_http_cookie(
    response: HTTPFrameworkResponse,
    key: str,
    httponly: bool = True,
) -> None:
    response.delete_cookie(
        key=key,
        domain=shared_config.eave_cookie_domain,
        path="/",
        httponly=httponly,
        secure=(not shared_config.is_development),
        samesite="lax",
    )
