from http.cookies import SimpleCookie
import typing
from datetime import datetime
from typing import Any, Literal, Protocol
from starlette.responses import Response

from .config import shared_config


class ResponseCookieMutator(Protocol):
    """
    This protocol is necessary because we pass in both Flask and Starlette response objects, which both
    have the same set_cookie signature but are different types.
    """

    # Copied from Starlette's set_cookie signature
    def set_cookie(
        self,
        key: str,
        value: str = "",
        max_age: typing.Optional[int] = None,
        expires: typing.Optional[typing.Union[datetime, str, int]] = None,
        path: str = "/",
        domain: typing.Optional[str] = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: typing.Optional[Literal["lax", "strict", "none"]] = "lax",
    ) -> Any:
        ...


def set_http_cookie(key: str, value: str, response: ResponseCookieMutator, httponly: bool = True) -> None:
    response.set_cookie(
        key=key,
        value=value,
        max_age=(60 * 60 * 24 * 365),
        domain=shared_config.eave_cookie_domain,
        httponly=httponly,
        secure=(not shared_config.is_development),
    )


def delete_http_cookie(response: ResponseCookieMutator, key: str, httponly: bool = True) -> None:
    response.set_cookie(
        key=key,
        value="",
        max_age=0,
        expires=0,
        domain=shared_config.eave_cookie_domain,
        httponly=httponly,
        secure=(not shared_config.is_development),
    )
