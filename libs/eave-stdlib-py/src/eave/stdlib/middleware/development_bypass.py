import uuid

import eave.stdlib
from eave.stdlib.config import shared_config
from asgiref.typing import HTTPScope

from eave.stdlib.request_state import EaveRequestState
from eave.stdlib.logging import eaveLogger

"""
## middleware check bypass

To bypass the signature and auth verification middlewares in development mode, the following conditions must be met:

1. `EAVE_ENV` must be set to "development"
1. Python "dev_mode" must be enabled. You can set `PYTHONDEVMODE=1` in your `.env` file to enable it.
1. The `GOOGLE_CLOUD_PROJECT` must not be set to `eave-production`.
1. A header `X-Google-EAVEDEV` exists on the request, and is set to the string you get from the following Python command:

```
$ python
>>> import os
>>> str(os.uname())
```

You'll get a string that looks something like this:

```
posix.uname_result(sysname='Linux', nodename='your computer name', release='OS release identifier', version='OS version identifier', machine='x86_64')
```

Copy that string into the `X-Google-EAVEDEV` header. It will be verified when requesting development bypass.

### Auth Bypass

When bypassing auth, the `Authorization` header should contain the ID of the account you want to act as.
"""
def development_bypass_allowed(scope: HTTPScope) -> bool:
    if not shared_config.is_development:
        return False
    if shared_config.google_cloud_project == "eave-production":
        return False

    dev_header = eave.stdlib.api_util.get_header_value(scope=scope, name=eave.stdlib.headers.EAVE_DEV_BYPASS_HEADER)
    if not dev_header:
        return False

    import os

    expected_uname = str(os.uname())
    if dev_header == expected_uname:
        eaveLogger.warning("Development bypass request accepted; some checks will be bypassed.")
        return True

    raise Exception()
