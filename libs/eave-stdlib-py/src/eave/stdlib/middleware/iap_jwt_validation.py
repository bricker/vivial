from typing import cast

import asgiref.typing
from google.auth.transport import requests
from google.oauth2 import id_token
from starlette.types import ASGIApp, Receive, Scope, Send

from eave.stdlib.api_util import get_header_value_or_exception
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.http_exceptions import ForbiddenError
from eave.stdlib.logging import LOGGER

IAP_JWT_HEADER = "x-goog-iap-jwt-assertion"


class IAPJWTValidationMiddleware:
    """
    https://cloud.google.com/iap/docs/signed-headers-howto
    """

    app: asgiref.typing.ASGI3Application
    aud: str
    enabled: bool

    def __init__(self, app: ASGIApp, *, aud: str, enabled: bool) -> None:
        self.app = cast(asgiref.typing.ASGI3Application, app)
        self.aud = aud
        self.enabled = enabled

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        cscope = cast(asgiref.typing.Scope, scope)
        creceive = cast(asgiref.typing.ASGIReceiveCallable, receive)
        csend = cast(asgiref.typing.ASGISendCallable, send)

        if cscope["type"] != "http":
            raise Exception(f"only HTTP requests are allowed ({cscope["type"]})")

        if cscope["path"] == "/healthz" or cscope["path"] == "/status":
            # Healthcheck endpoints always allowed
            await self.app(cscope, creceive, csend)
            return

        if self.enabled:
            if not self.aud:
                raise ForbiddenError("IAP auth failed (missing audience)")

            jwt_assertion_header = get_header_value_or_exception(scope=cscope, name=IAP_JWT_HEADER)

            decoded_token = id_token.verify_token(
                jwt_assertion_header,
                requests.Request(),
                audience=self.aud,
                certs_url="https://www.gstatic.com/iap/verify/public_key",
            )

            email = decoded_token["email"]
            sub = decoded_token["sub"]
            if not email or not sub:
                LOGGER.warning("IAP auth failed", decoded_token)
                raise ForbiddenError("IAP auth failed")

            LOGGER.info("Admin authenticated through IAP", decoded_token)

        await self.app(cscope, creceive, csend)
