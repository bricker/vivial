import eave_stdlib.util as eave_util
from eave_core.internal.config import app_config

def shared_state_cookie_params() -> eave_util.JsonObject:
    params = {
        "key": "ev_oauth_state",
        "domain": app_config.eave_cookie_domain,
        "secure": True,
        "httponly": True,
    }

    return params
