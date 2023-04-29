from datetime import datetime
from typing import Any, Generic, Literal, Mapping, Protocol, TypeVar
import typing
from . import headers as eave_headers
from . import jwt as eave_jwt
from .core_api import models as eave_models
from .config import shared_config

T = TypeVar("T")

class ResponseCookieMutator(Protocol):
    # Copied from FastAPI's set_cookie signature
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

_shared_cookie_config = {
    "domain":shared_config.eave_cookie_domain,
    "httponly":True,
    "secure":shared_config.dev_mode is False
}

def get_auth_cookies(cookies: Mapping[str, Any]) -> eave_models.AuthTokenPair:
    access_token = cookies.get(eave_headers.EAVE_ACCESS_TOKEN_COOKIE)
    refresh_token = cookies.get(eave_headers.EAVE_REFRESH_TOKEN_COOKIE)
    return eave_models.AuthTokenPair(access_token=str(access_token), refresh_token=str(refresh_token))

def set_auth_cookies(response: ResponseCookieMutator, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        key=eave_headers.EAVE_ACCESS_TOKEN_COOKIE,
        value=access_token,
        max_age=(60*60*24*365),
        domain=shared_config.eave_cookie_domain,
        httponly=True,
        secure=(shared_config.dev_mode is False),
    )

    response.set_cookie(
        key=eave_headers.EAVE_REFRESH_TOKEN_COOKIE,
        value=refresh_token,
        max_age=(60*60*24*365),
        domain=shared_config.eave_cookie_domain,
        httponly=True,
        secure=(shared_config.dev_mode is False),
    )

def delete_auth_cookies(response: ResponseCookieMutator) -> None:
    response.set_cookie(
        key=eave_headers.EAVE_ACCESS_TOKEN_COOKIE,
        value="",
        max_age=0,
        expires=0,
        domain=shared_config.eave_cookie_domain,
        httponly=True,
        secure=(shared_config.dev_mode is False),
    )

    response.set_cookie(
        key=eave_headers.EAVE_REFRESH_TOKEN_COOKIE,
        value="",
        max_age=0,
        expires=0,
        domain=shared_config.eave_cookie_domain,
        httponly=True,
        secure=(shared_config.dev_mode is False),
    )
