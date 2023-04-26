from . import asgi_types
from eave.stdlib.config import shared_config
import eave.stdlib.core_api.headers as eave_headers
import eave.core.public.requests.util as request_util
class EaveASGIMiddleware:
    """
    https://asgi.readthedocs.io/en/latest/specs/www.html#http
    """

    app: asgi_types.ASGIFramework

    def __init__(self, app: asgi_types.ASGIFramework) -> None:
        self.app = app

    async def __call__(
        self, scope: asgi_types.Scope, receive: asgi_types.ASGIReceiveCallable, send: asgi_types.ASGISendCallable
    ) -> None:
        ...

    @staticmethod
    def development_bypass_allowed(scope: asgi_types.HTTPScope) -> bool:
        if not shared_config.dev_mode:
            return False
        if shared_config.google_cloud_project == "eave-production":
            return False

        dev_header = request_util.get_header_value(scope=scope, name=eave_headers.EAVE_DEV_BYPASS_HEADER)
        if not dev_header:
            return False

        import os
        expected_uname = str(os.uname())
        if dev_header == expected_uname:
            return True

        raise Exception()