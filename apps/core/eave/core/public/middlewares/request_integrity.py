import uuid

import eave.stdlib
from asgiref.typing import ASGIReceiveCallable, ASGISendCallable, Scope

import eave.core.public
from . import EaveASGIMiddleware

ALLOWED_ASGI_PROTOCOLS = ["http", "lifespan"]


class RequestIntegrityASGIMiddleware(EaveASGIMiddleware):
    """
    Does some basic integrity checks, for example:
    - the request is for a supported protocol
    - the ASGI scope["state"] property is set.
    - a request_id is set on the request
    """

    async def __call__(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        if scope["type"] not in ALLOWED_ASGI_PROTOCOLS:
            raise eave.stdlib.exceptions.BadRequestError(f"Unsupported protocol: {scope['type']}")

        if scope["type"] == "http":
            with self.auto_eave_state(scope=scope) as eave_state:
                request_id_header = eave.stdlib.api_util.get_header_value(
                    scope=scope, name=eave.stdlib.headers.EAVE_REQUEST_ID_HEADER
                )

                if not request_id_header:
                    request_id = str(uuid.uuid4())
                else:
                    request_id = request_id_header

                eave_state.request_id = request_id
                eave_state.request_method = scope["method"]
                eave_state.request_scheme = scope["scheme"]
                eave_state.request_path = scope["path"]
                eave_state.request_headers = eave.stdlib.api_util.get_headers(
                    scope,
                    redact=[eave.stdlib.headers.EAVE_COOKIE_HEADER, eave.stdlib.headers.EAVE_AUTHORIZATION_HEADER],
                )

        await self.app(scope, receive, send)
