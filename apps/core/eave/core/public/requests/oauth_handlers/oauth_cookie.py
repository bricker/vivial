import fastapi
from eave.core.internal.config import app_config


# oauth cookie helpers
STATE_COOKIE_NAME = "eave-oauth-state"
STATE_COOKIE_PARAMS = {
    "key": STATE_COOKIE_NAME,
    "domain": "fa6b-2601-281-8100-82b0-00-928.ngrok.io", # TODO: app_config.eave_cookie_domain,
    "secure": True,
    "httponly": True,
}


def save_state_cookie(response: fastapi.responses.Response, state: str) -> None:
    response.set_cookie(
        **STATE_COOKIE_PARAMS,
        value=state,
    )


def get_state_cookie(request: fastapi.Request) -> str:
    state: str | None = request.cookies.get(STATE_COOKIE_NAME)
    assert state is not None
    return state


def delete_state_cookie(response: fastapi.responses.Response) -> None:
    response.delete_cookie(**STATE_COOKIE_PARAMS)
