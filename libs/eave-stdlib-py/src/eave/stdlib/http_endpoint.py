from abc import abstractmethod
import abc
import typing

import asgiref.typing
from eave.stdlib.request_state import EaveRequestState
import starlette.types
from starlette._utils import is_async_callable
from starlette.concurrency import run_in_threadpool
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response


class HTTPEndpoint:
    scope: asgiref.typing.HTTPScope
    receive: asgiref.typing.ASGIReceiveCallable
    send: asgiref.typing.ASGISendCallable
    request: Request
    state: EaveRequestState

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

        self.state = EaveRequestState.load(request=self.request)

    def __await__(self) -> typing.Generator[typing.Any, None, None]:
        return self._dispatch().__await__()

    async def handle(self, request: Request, scope: asgiref.typing.HTTPScope, state: EaveRequestState) -> Response:
        raise NotImplementedError("HTTPEndpoint.handler")

    async def _dispatch(self) -> None:
        response = await self.handle(
            request=self.request,
            scope=self.scope,
            state=self.state
        )

        await response(
            typing.cast(starlette.types.Scope, self.scope),
            typing.cast(starlette.types.Receive, self.receive),
            typing.cast(starlette.types.Send, self.send),
        )
