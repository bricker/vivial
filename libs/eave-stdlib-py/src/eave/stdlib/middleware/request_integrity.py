from typing import Awaitable, Callable
from uuid import uuid4
import asgiref.typing
from eave.stdlib.api_util import get_header_value
from eave.stdlib.headers import EAVE_REQUEST_ID_HEADER
from eave.stdlib.logging import LogContext
from starlette.requests import Request

from ..exceptions import BadRequestError
from .base import EaveASGIMiddleware

_ALLOWED_ASGI_PROTOCOLS = ["http", "lifespan"]


class RequestIntegrityASGIMiddleware(EaveASGIMiddleware):
    """
    Does some basic integrity checks
    """

    async def process_request(
        self,
        scope: asgiref.typing.HTTPScope,
        receive: asgiref.typing.ASGIReceiveCallable,
        send: asgiref.typing.ASGISendCallable,
        request: Request,
        ctx: LogContext,
        continue_request: Callable[[], Awaitable[None]],
    ) -> None:
        if request_id_header := get_header_value(scope=scope, name=EAVE_REQUEST_ID_HEADER):
            ctx.eave_request_id = request_id_header

        await continue_request()

    async def handle(
        self,
        scope: asgiref.typing.Scope,
        receive: asgiref.typing.ASGIReceiveCallable,
        send: asgiref.typing.ASGISendCallable,
    ) -> None:
        if scope["type"] not in _ALLOWED_ASGI_PROTOCOLS:
            raise BadRequestError(f"Unsupported protocol: {scope['type']}")

        await super().handle(scope, receive, send)
