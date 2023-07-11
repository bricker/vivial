from dataclasses import dataclass
from typing import Mapping, Optional
import uuid

from eave.stdlib.cookies import ResponseCookieMutator, delete_http_cookie, set_http_cookie

_EAVE_ACCOUNT_ID_COOKIE = "ev_account_id"
_EAVE_ACCESS_TOKEN_COOKIE = "ev_access_token"

@dataclass
class AuthCookies:
    account_id: Optional[str]
    access_token: Optional[str]

def set_auth_cookies(
    response: ResponseCookieMutator,
    account_id: Optional[uuid.UUID | str] = None,
    access_token: Optional[str] = None,
) -> None:
    if account_id:
        set_http_cookie(key=_EAVE_ACCOUNT_ID_COOKIE, value=str(account_id), response=response)

    if access_token:
        set_http_cookie(key=_EAVE_ACCESS_TOKEN_COOKIE, value=access_token, response=response)

def get_auth_cookies(cookies: Mapping[str, str]) -> AuthCookies:
    account_id = cookies.get(_EAVE_ACCOUNT_ID_COOKIE)
    access_token = cookies.get(_EAVE_ACCESS_TOKEN_COOKIE)

    return AuthCookies(
        account_id=account_id,
        access_token=access_token,
    )


def delete_auth_cookies(response: ResponseCookieMutator) -> None:
    delete_http_cookie(response=response, key=_EAVE_ACCOUNT_ID_COOKIE)
    delete_http_cookie(response=response, key=_EAVE_ACCESS_TOKEN_COOKIE)
