from abc import ABC
from collections.abc import Awaitable, Callable
from typing import cast

import asgiref.typing
import starlette.types
from starlette.requests import Request

from eave.stdlib.logging import LogContext


class EaveASGIMiddleware(ABC):
    """
    https://asgi.readthedocs.io/en/latest/specs/www.html#http
    """

    app: asgiref.typing.ASGI3Application

    def __init__(self, app: asgiref.typing.ASGI3Application) -> None:
        self.app = cast(asgiref.typing.ASGI3Application, app)

    async def process_request(
        self,
        scope: asgiref.typing.HTTPScope,
        receive: asgiref.typing.ASGIReceiveCallable,
        send: asgiref.typing.ASGISendCallable,
        request: Request,
        ctx: LogContext,
        continue_request: Callable[[], Awaitable[None]],
    ) -> None:
        """
        Processes the request. This is the main entrypoint for sublcasses.
        Override this function with your middleware logic.
        The default implementation just continues the request (pass-through)
        """
        # Default implementation just continues
        await continue_request()

    async def handle(
        self,
        scope: asgiref.typing.Scope,
        receive: asgiref.typing.ASGIReceiveCallable,
        send: asgiref.typing.ASGISendCallable,
    ) -> None:
        """
        Lower-level function to do some basic checks and create the Request and LogContext objects.
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        cscope = cast(starlette.types.Scope, scope)
        creceive = cast(starlette.types.Receive, receive)

        request = Request(scope=cscope, receive=creceive)
        ctx = LogContext.load(scope=cscope)

        async def _next_handler() -> None:
            await self.app(scope, receive, send)

        await self.process_request(
            scope=scope,
            receive=receive,
            send=send,
            request=request,
            ctx=ctx,
            continue_request=_next_handler,
        )

    async def __call__(
        self,
        scope: asgiref.typing.Scope,
        receive: asgiref.typing.ASGIReceiveCallable,
        send: asgiref.typing.ASGISendCallable,
    ) -> None:
        """
        Just casts the scope, receive, and send objects to more useful types.
        """
        await self.handle(
            scope=cast(asgiref.typing.Scope, scope),
            receive=cast(asgiref.typing.ASGIReceiveCallable, receive),
            send=cast(asgiref.typing.ASGISendCallable, send),
        )
