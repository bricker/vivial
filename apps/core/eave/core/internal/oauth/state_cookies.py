from typing import Any

from starlette.requests import Request
from starlette.responses import Response

from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.cookies import EAVE_OAUTH_STATE_COOKIE_PREFIX
from eave.stdlib.core_api.models.account import AuthProvider
from eave.stdlib.exceptions import UnexpectedMissingValueError


def _build_cookie_name(provider: AuthProvider) -> str:
    return f"{EAVE_OAUTH_STATE_COOKIE_PREFIX}{provider.value}"


def save_state_cookie(response: Response, state: str, provider: AuthProvider) -> None:
    response.set_cookie(
        key=_build_cookie_name(provider=provider),
        value=state,
        domain=SHARED_CONFIG.eave_cookie_domain,
        path=f"/oauth/{provider.value}/callback",
        secure=True,
        httponly=True,
        samesite="lax",
    )


def get_state_cookie(request: Request, provider: AuthProvider) -> str:
    state: str | None = request.cookies.get(_build_cookie_name(provider))
    if state is None:
        raise UnexpectedMissingValueError(f"state cookie for {provider.value}")

    return state


def delete_state_cookie(response: Response, provider: AuthProvider) -> None:
    response.delete_cookie(
        key=_build_cookie_name(provider=provider),
        domain=SHARED_CONFIG.eave_cookie_domain,
        path=f"/oauth/{provider.value}/callback",
        secure=True,
        httponly=True,
        samesite="lax",
    )
