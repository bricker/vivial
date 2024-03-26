from asgiref.typing import HTTPScope

from ..api_util import get_header_value
from ..config import SHARED_CONFIG
from ..headers import EAVE_DEV_BYPASS_HEADER

"""
## middleware check bypass

To bypass the signature and auth verification middlewares in development mode, the following conditions must be met:

1. `EAVE_ENV` must be set to "development"
1. Python "dev_mode" must be enabled. You can set `PYTHONDEVMODE=1` in your `.env` file to enable it.
1. The `GOOGLE_CLOUD_PROJECT` must not be set to `eave-production`.
1. A header `X-Google-EAVEDEV` is set to "1"

### Auth Bypass

When bypassing auth, the `Authorization` header should contain the ID of the account you want to act as.
"""


def development_bypass_allowed(scope: HTTPScope) -> bool:
    if not SHARED_CONFIG.is_development:
        return False
    if not SHARED_CONFIG.dev_mode:
        return False
    if SHARED_CONFIG.google_cloud_project == "eave-production":
        return False

    dev_header = get_header_value(scope=scope, name=EAVE_DEV_BYPASS_HEADER)
    if not dev_header:
        return False

    if dev_header == "1":
        return True

    raise Exception("development bypass failed")
