import re
import typing
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, Mapping, Protocol

from .config import shared_config

EAVE_COOKIE_PREFIX_UTM = "ev_utm_"
EAVE_VISITOR_ID_COOKIE = "ev_visitor_id"
EAVE_ACCOUNT_ID_COOKIE = "ev_account_id"
EAVE_ACCESS_TOKEN_COOKIE = "ev_access_token"


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


@dataclass
class TrackingCookies:
    utm_params: typing.Optional[typing.Dict[str, str]]
    visitor_id: typing.Optional[uuid.UUID]


def get_tracking_cookies(cookies: Mapping[str, str]) -> TrackingCookies:
    visitor_id = cookies.get(EAVE_VISITOR_ID_COOKIE)
    utm_params: typing.Dict[str, str] = {}

    for key, value in cookies.items():
        if re.match(EAVE_COOKIE_PREFIX_UTM, key):
            utm_param_name = re.sub(f"^{EAVE_COOKIE_PREFIX_UTM}", "", key)
            utm_params[utm_param_name] = value

    return TrackingCookies(
        utm_params=utm_params,
        visitor_id=uuid.UUID(visitor_id) if visitor_id else None,
    )


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
        secure=(not shared_config.is_development),
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
        secure=(not shared_config.is_development),
    )
