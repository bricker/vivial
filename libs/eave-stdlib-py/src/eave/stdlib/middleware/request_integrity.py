import asgiref.typing

from ..exceptions import BadRequestError
from .base import EaveASGIMiddleware

_ALLOWED_ASGI_PROTOCOLS = ["http", "lifespan"]


class RequestIntegrityASGIMiddleware(EaveASGIMiddleware):
    """
    Does some basic integrity checks, for example:
    - the request is for a supported protocol
    """

    # This class overrides the __call__() method instead of run() so that it can perform lower-level checks on the request
    # than EaveASGIMiddleware allows.
    async def handle(
        self,
        scope: asgiref.typing.Scope,
        receive: asgiref.typing.ASGIReceiveCallable,
        send: asgiref.typing.ASGISendCallable,
    ) -> None:
        if scope["type"] not in _ALLOWED_ASGI_PROTOCOLS:
            raise BadRequestError(f"Unsupported protocol: {scope['type']}")

        await super().handle(scope, receive, send)
