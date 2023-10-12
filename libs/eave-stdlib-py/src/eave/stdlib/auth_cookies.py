from dataclasses import dataclass
from http.cookies import Morsel, SimpleCookie
from typing import Mapping, Optional
import uuid


from eave.stdlib.cookies import ResponseCookieMutator, delete_http_cookie, set_http_cookie

_EAVE_ACCOUNT_ID_COOKIE = "ev_account_id"
_EAVE_TEAM_ID_COOKIE = "ev_team_id"
_EAVE_ACCESS_TOKEN_COOKIE = "ev_access_token"


@dataclass
class AuthCookies:
    account_id: Optional[str]
    team_id: Optional[str]
    access_token: Optional[str]


def set_auth_cookies(
    response: ResponseCookieMutator,
    account_id: Optional[uuid.UUID | str] = None,
    team_id: Optional[uuid.UUID | str] = None,
    access_token: Optional[str] = None,
) -> None:
    if account_id:
        set_http_cookie(key=_EAVE_ACCOUNT_ID_COOKIE, value=str(account_id), response=response)

    if team_id:
        set_http_cookie(key=_EAVE_TEAM_ID_COOKIE, value=str(team_id), response=response)

    if access_token:
        set_http_cookie(key=_EAVE_ACCESS_TOKEN_COOKIE, value=access_token, response=response)


def get_auth_cookies(cookies: SimpleCookie | Mapping[str, str]) -> AuthCookies:
    account_id = cookies.get(_EAVE_ACCOUNT_ID_COOKIE)
    team_id = cookies.get(_EAVE_TEAM_ID_COOKIE)
    access_token = cookies.get(_EAVE_ACCESS_TOKEN_COOKIE)

    return AuthCookies(
        account_id=account_id.value if isinstance(account_id, Morsel) else account_id,
        team_id=team_id.value if isinstance(team_id, Morsel) else team_id,
        access_token=access_token.value if isinstance(access_token, Morsel) else access_token,
    )


def delete_auth_cookies(response: ResponseCookieMutator) -> None:
    delete_http_cookie(response=response, key=_EAVE_ACCOUNT_ID_COOKIE)
    delete_http_cookie(response=response, key=_EAVE_TEAM_ID_COOKIE)
    delete_http_cookie(response=response, key=_EAVE_ACCESS_TOKEN_COOKIE)
