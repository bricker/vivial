from functools import cache
from typing import Any, cast
import aiohttp
from joserfc import jwt, jwk
from google.oauth2 import id_token
from google.auth.transport import Request
import asgiref.typing
import requests
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.requests import Request as StarletteRequest

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

    def __init__(self, app: ASGIApp, *, aud: str) -> None:
        self.app = cast(asgiref.typing.ASGI3Application, app)
        self.aud = aud

    async def __call__(
        self,
        _scope: Scope,
        _receive: Receive,
        _send: Send,
    ) -> None:
        scope = cast(asgiref.typing.Scope, _scope)
        receive = cast(asgiref.typing.ASGIReceiveCallable, _receive)
        send = cast(asgiref.typing.ASGISendCallable, _send)

        if scope["type"] != "http":
            raise Exception(f"only HTTP requests are allowed ({scope["type"]})")

        if scope["path"] == "/healthz":
            await self.app(scope, receive, send)

        # key_set = await _get_jwk_public_keys()

        # claims_requests = jwt.JWTClaimsRegistry(
        #     alg={"essential": True, "value": "ES256"},
        #     kid={"essential": True, "values": [k.kid for k in key_set.keys if k.kid is not None]},
        #     aud={"essential": True, "value": self.aud},
        #     iss={"essential": True, "value": "https://cloud.google.com/iap"},
        # )

        if not SHARED_CONFIG.is_local:
            jwt_assertion_header = get_header_value_or_exception(scope=scope, name=IAP_JWT_HEADER)

            # token = jwt.decode(jwt_assertion_header, key=key_set)
            # claims_requests.validate(token.claims) # Raises for invalid JWT

            decoded_token = id_token.verify_token(
                jwt_assertion_header,
                requests.Request(),
                audience=self.aud,
                certs_url="https://www.gstatic.com/iap/verify/public_key",
            )

            email = decoded_token["email"]
            sub = decoded_token["sub"]
            if not email or not sub:
                raise ForbiddenError("IAP auth failed")

            LOGGER.info("Admin authenticated through IAP", decoded_token)

        await self.app(scope, receive, send)

# @cache
# async def _get_jwk_public_keys() -> jwk.KeySet:
#     async with aiohttp.ClientSession(raise_for_status=True) as session:
#         response = await session.request(
#             method=aiohttp.hdrs.METH_GET,
#             url="https://www.gstatic.com/iap/verify/public_key-jwk",
#         )

#         # Consume the body while the session is still open
#         body = await response.json()

#     return jwk.KeySet.import_key_set(body)
