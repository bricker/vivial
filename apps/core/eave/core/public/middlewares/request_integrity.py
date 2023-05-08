from typing import cast
import uuid

import eave.stdlib.exceptions as eave_exceptions
import eave.stdlib.headers as eave_headers
from eave.stdlib import logger, api_util
from asgiref.typing import Scope, ASGIReceiveCallable, ASGISendCallable

from .. import request_state as request_util
from . import EaveASGIMiddleware

ALLOWED_ASGI_PROTOCOLS = ["http", "lifespan"]


class RequestIntegrityASGIMiddleware(EaveASGIMiddleware):
    """
    Does some basic integrity checks, for example:
    - the request is for a supported protocol
    - the ASGI scope["state"] property is set.
    - a request_id is set on the request
    """

    async def __call__(
        self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None:
        if scope["type"] not in ALLOWED_ASGI_PROTOCOLS:
            raise eave_exceptions.BadRequestError(f"Unsupported protocol: {scope['type']}")

        # Ensure that scope["state"] is available as early as possible.
        # Starlette does this too, but too late in the cycle.
        scope.setdefault("state", {})

        if scope["type"] == "http":
            request_id_header = api_util.get_header_value(scope=scope, name=eave_headers.EAVE_REQUEST_ID_HEADER)

            if not request_id_header:
                request_id = uuid.uuid4()
            else:
                request_id = uuid.UUID(request_id_header)

            eave_state = request_util.get_eave_state(scope)
            eave_state.request_id = request_id
            logger.info(f"Request: {eave_state.request_path}", extra=eave_state.log_context)

        await self.app(scope, receive, send)
