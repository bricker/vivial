from math import log
import typing
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, Mapping, Protocol

from .config import shared_config

EAVE_ACCOUNT_ID_COOKIE = "ev_account_id"
EAVE_ACCESS_TOKEN_COOKIE = "ev_access_token"


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
    "domain": shared_config.eave_cookie_domain,
    "httponly": True,
    "secure": shared_config.dev_mode is False,
}


@dataclass
class AuthCookies:
    account_id: typing.Optional[uuid.UUID]
    access_token: typing.Optional[str]


def get_auth_cookies(cookies: Mapping[str, str]) -> AuthCookies:
    account_id = cookies.get(EAVE_ACCOUNT_ID_COOKIE)
    access_token = cookies.get(EAVE_ACCESS_TOKEN_COOKIE)

    return AuthCookies(
        account_id=uuid.UUID(account_id) if account_id else None,
        access_token=access_token,
    )


def set_auth_cookies(
    response: ResponseCookieMutator,
    account_id: typing.Optional[uuid.UUID] = None,
    access_token: typing.Optional[str] = None,
) -> None:
    if account_id:
        _set_auth_cookie(key=EAVE_ACCOUNT_ID_COOKIE, value=str(account_id), response=response)

    if access_token:
        _set_auth_cookie(key=EAVE_ACCESS_TOKEN_COOKIE, value=access_token, response=response)


def _set_auth_cookie(key: str, value: str, response: ResponseCookieMutator) -> None:
    response.set_cookie(
        key=key,
        value=value,
        max_age=(60 * 60 * 24 * 365),
        domain=shared_config.eave_cookie_domain,
        httponly=True,
        secure=(shared_config.dev_mode is False),
    )


def delete_auth_cookies(response: ResponseCookieMutator) -> None:
    _delete_auth_cookie(response=response, key=EAVE_ACCOUNT_ID_COOKIE)
    _delete_auth_cookie(response=response, key=EAVE_ACCESS_TOKEN_COOKIE)


def _delete_auth_cookie(response: ResponseCookieMutator, key: str) -> None:
    response.set_cookie(
        key=key,
        value="",
        max_age=0,
        expires=0,
        domain=shared_config.eave_cookie_domain,
        httponly=True,
        secure=(shared_config.dev_mode is False),
    )
