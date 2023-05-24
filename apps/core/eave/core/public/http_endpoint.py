import typing

import starlette.types
from asgiref.typing import ASGIReceiveCallable, ASGISendCallable, Scope
from starlette._utils import is_async_callable
from starlette.concurrency import run_in_threadpool
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response


class HTTPEndpoint:
    """
    Copy of starlette's HTTPEndpoint, but with better typing.
    """

    def __init__(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        assert scope["type"] == "http", "only http type supported"
        self.scope = scope
        self.receive = receive
        self.send = send
        self._allowed_methods = [
            method
            for method in ("GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")
            if getattr(self, method.lower(), None) is not None
        ]

    def __await__(self) -> typing.Generator[typing.Any, None, None]:
        return self.dispatch().__await__()

    async def dispatch(self) -> None:
        _scope = typing.cast(starlette.types.Scope, self.scope)
        _receive = typing.cast(starlette.types.Receive, self.receive)
        _send = typing.cast(starlette.types.Send, self.send)

        request = Request(
            scope=_scope,
            receive=_receive,
        )

        handler_name = "get" if request.method == "HEAD" and not hasattr(self, "head") else request.method.lower()

        handler: typing.Callable[[Request], typing.Any] = getattr(self, handler_name, self.method_not_allowed)
        is_async = is_async_callable(handler)
        if is_async:
            response = await handler(request)
        else:
            coro = await run_in_threadpool(handler, request)
            response = await coro

        await response(_scope, _receive, _send)

    async def method_not_allowed(self, request: Request) -> Response:
        # If we're running inside a starlette application then raise an
        # exception, so that the configurable exception handler can deal with
        # returning the response. For plain ASGI apps, just return the response.
        headers = {"Allow": ", ".join(self._allowed_methods)}
        if "app" in self.scope:
            raise HTTPException(status_code=405, headers=headers)
        return PlainTextResponse("Method Not Allowed", status_code=405, headers=headers)
