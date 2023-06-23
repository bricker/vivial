from asgiref.typing import ASGIReceiveCallable, ASGISendCallable, Scope


from .base import EaveASGIMiddleware
from ..exceptions import BadRequestError

ALLOWED_ASGI_PROTOCOLS = ["http", "lifespan"]


class RequestIntegrityASGIMiddleware(EaveASGIMiddleware):
    """
    Does some basic integrity checks, for example:
    - the request is for a supported protocol
    """

    async def __call__(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        if scope["type"] not in ALLOWED_ASGI_PROTOCOLS:
            raise BadRequestError(f"Unsupported protocol: {scope['type']}")

        await self.app(scope, receive, send)
