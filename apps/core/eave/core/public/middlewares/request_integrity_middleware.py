import uuid

import eave.stdlib.core_api.headers as eave_headers
import eave.stdlib.exceptions as eave_exceptions

from ..requests import util as request_util
from . import EaveASGIMiddleware, asgi_types

ALLOWED_ASGI_PROTOCOLS = ["http", "lifespan"]


class RequestIntegrityASGIMiddleware(EaveASGIMiddleware):
    """
    Does some basic integrity checks, for example:
    - the request is for a supported protocol
    - the ASGI scope["state"] property is set.
    - a request_id is set on the request
    """

    async def __call__(
        self, scope: asgi_types.Scope, receive: asgi_types.ASGIReceiveCallable, send: asgi_types.ASGISendCallable
    ) -> None:
        if scope["type"] not in ALLOWED_ASGI_PROTOCOLS:
            raise eave_exceptions.BadRequestError(f"Unsupported protocol: {scope['type']}")

        # Ensure that scope["state"] is available as early as possible.
        # Starlette does this too, but too late in the cycle.
        scope.setdefault("state", {})

        if scope["type"] == "http":
            request_id_header = request_util.get_header_value(scope=scope, name=eave_headers.EAVE_REQUEST_ID_HEADER)

            if not request_id_header:
                request_id = uuid.uuid4()
            else:
                request_id = uuid.UUID(request_id_header)

            request_util.get_eave_state(scope).request_id = request_id

        await self.app(scope, receive, send)
