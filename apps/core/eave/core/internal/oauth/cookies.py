from typing import Any

import fastapi

from ..config import app_config
import eave.stdlib.core_api.models as eave_models


def _build_cookie_name(postfix: str) -> str:
    return f"eave-oauth-state-{postfix}"


def _build_cookie_params(cookie_postfix: str) -> dict[str, Any]:
    return {
        "key": _build_cookie_name(cookie_postfix),
        "domain": app_config.eave_cookie_domain,
        "secure": app_config.dev_mode is False,
        "httponly": True,
    }


def save_state_cookie(response: fastapi.responses.Response, state: str, provider: eave_models.AuthProvider) -> None:
    response.set_cookie(
        **_build_cookie_params(provider.value),
        value=state,
    )


def get_state_cookie(request: fastapi.Request, provider: eave_models.AuthProvider) -> str:
    state: str | None = request.cookies.get(_build_cookie_name(provider.value))
    assert state is not None
    return state


def delete_state_cookie(response: fastapi.responses.Response, provider: eave_models.AuthProvider) -> None:
    response.delete_cookie(**_build_cookie_params(provider.value))
