from dataclasses import dataclass
from http.cookies import Morsel, SimpleCookie
from typing import Mapping, Optional
import uuid


from eave.stdlib.cookies import delete_http_cookie, set_http_cookie
from eave.stdlib.typing import HTTPFrameworkResponse

_EAVE_ACCOUNT_ID_COOKIE = "ev_account_id"
_EAVE_TEAM_ID_COOKIE = "ev_team_id"
_EAVE_ACCESS_TOKEN_COOKIE = "ev_access_token"


@dataclass
class AuthCookies:
    account_id: Optional[str]
    team_id: Optional[str]
    access_token: Optional[str]


def get_auth_cookies(cookies: SimpleCookie | Mapping[str, str]) -> AuthCookies:
    account_id = cookies.get(_EAVE_ACCOUNT_ID_COOKIE)
    team_id = cookies.get(_EAVE_TEAM_ID_COOKIE)
    access_token = cookies.get(_EAVE_ACCESS_TOKEN_COOKIE)

    account_id_decoded = account_id.value if isinstance(account_id, Morsel) else account_id
    team_id_decoded = team_id.value if isinstance(team_id, Morsel) else team_id
    access_token_decoded = access_token.value if isinstance(access_token, Morsel) else access_token

    return AuthCookies(
        account_id=account_id_decoded,
        team_id=team_id_decoded,
        access_token=access_token_decoded,
    )


def set_auth_cookies(
    response: HTTPFrameworkResponse,
    account_id: Optional[uuid.UUID | str] = None,
    team_id: Optional[uuid.UUID | str] = None,
    access_token: Optional[str] = None,
) -> None:
    if account_id:
        set_http_cookie(response=response, key=_EAVE_ACCOUNT_ID_COOKIE, value=str(account_id))

    if team_id:
        set_http_cookie(response=response, key=_EAVE_TEAM_ID_COOKIE, value=str(team_id))

    if access_token:
        # We base64-encode this value because its format is unknown to us, and cookies with unsafe characters (eg spaces) have unexpected behavior (eg, the value is wrapped in quotes).
        set_http_cookie(response=response, key=_EAVE_ACCESS_TOKEN_COOKIE, value=access_token)


def delete_auth_cookies(response: HTTPFrameworkResponse) -> None:
    delete_http_cookie(response=response, key=_EAVE_ACCOUNT_ID_COOKIE)
    delete_http_cookie(response=response, key=_EAVE_TEAM_ID_COOKIE)
    delete_http_cookie(response=response, key=_EAVE_ACCESS_TOKEN_COOKIE)
