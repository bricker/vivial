from typing import cast
# from starlette.types import ASGIApp, Scope, Receive, Send
from starlette.responses import Response
from asgiref.typing import ASGI3Application, Scope, ASGIReceiveCallable, ASGISendCallable

class EaveASGIMiddleware:
    """
    https://asgi.readthedocs.io/en/latest/specs/www.html#http
    """

    app: ASGI3Application

    def __init__(self, app: ASGI3Application) -> None:
        self.app = app

    async def __call__(
        self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None:
        ...
        # tscope = cast(Scope, scope)
        # treceive = cast(ASGIReceiveCallable, receive)
        # tsend = cast(ASGISendCallable, send)
        # await self.run(tscope, treceive, tsend)

    # async def run(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
    #     ...

    # async def proceed(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> Response:
    #     response = await self.app(
    #         cast(Scope, scope),
    #         cast(Receive, receive),
    #         cast(Send, send),
    #     )

    #     return response