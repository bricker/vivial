from typing import Any

import eave.stdlib.core_api.enums as eave_enums
import fastapi

from ..config import app_config


def _build_cookie_name(provider: eave_enums.AuthProvider) -> str:
    return f"ev_oauth_state_{provider.value}"


def _build_cookie_params(provider: eave_enums.AuthProvider) -> dict[str, Any]:
    return {
        "domain": app_config.eave_cookie_domain,
        "path": f"/oauth/{provider.value}/callback",
        "secure": app_config.dev_mode is False,
        "httponly": True,
        "samesite": "lax",
    }


# FIXME: This only works if provider.value matches the path for /oauth/{provider}/callback, which is a bold assumption!
def save_state_cookie(response: fastapi.responses.Response, state: str, provider: eave_enums.AuthProvider) -> None:
    response.set_cookie(
        key=_build_cookie_name(provider=provider),
        value=state,
        **_build_cookie_params(provider=provider),
    )


def get_state_cookie(request: fastapi.Request, provider: eave_enums.AuthProvider) -> str:
    state: str | None = request.cookies.get(_build_cookie_name(provider))
    assert state is not None
    return state


def delete_state_cookie(response: fastapi.responses.Response, provider: eave_enums.AuthProvider) -> None:
    response.delete_cookie(key=_build_cookie_name(provider=provider), **_build_cookie_params(provider))
