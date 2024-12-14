import typing

import asgiref.typing
import starlette.types
from starlette.requests import Request
from starlette.responses import Response


class HTTPEndpoint:
    scope: asgiref.typing.HTTPScope
    receive: asgiref.typing.ASGIReceiveCallable
    send: asgiref.typing.ASGISendCallable
    request: Request

    def __init__(
        self,
        scope: asgiref.typing.Scope,
        receive: asgiref.typing.ASGIReceiveCallable,
        send: asgiref.typing.ASGISendCallable,
    ) -> None:
        assert scope["type"] == "http", "only http type supported"
        self.scope = scope
        self.receive = receive
        self.send = send

        self.request = Request(
            scope=typing.cast(starlette.types.Scope, self.scope),
            receive=typing.cast(starlette.types.Receive, self.receive),
        )

    def __await__(self) -> typing.Generator[typing.Any, None, None]:
        return self._dispatch().__await__()

    async def handle(self, request: Request, scope: asgiref.typing.HTTPScope) -> Response:
        raise NotImplementedError("HTTPEndpoint.handler")

    async def _dispatch(self) -> None:
        response = await self.handle(request=self.request, scope=self.scope)

        await response(
            typing.cast(starlette.types.Scope, self.scope),
            typing.cast(starlette.types.Receive, self.receive),
            typing.cast(starlette.types.Send, self.send),
        )
