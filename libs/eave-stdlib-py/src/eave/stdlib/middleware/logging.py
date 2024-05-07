import time
from typing import Awaitable, Callable
from starlette.requests import Request
import asgiref.typing

from eave.stdlib.request_state import EaveRequestState

from ..logging import eaveLogger
from .base import EaveASGIMiddleware


class LoggingASGIMiddleware(EaveASGIMiddleware):
    async def process_request(
        self,
        scope: asgiref.typing.HTTPScope,
        receive: asgiref.typing.ASGIReceiveCallable,
        send: asgiref.typing.ASGISendCallable,
        request: Request,
        state: EaveRequestState,
        continue_request: Callable[[], Awaitable[None]],
    ) -> None:
        eaveLogger.info(
            f"Server Request Start: {state.ctx.eave_request_id}: {scope['method']} {scope['path']}",
            state.ctx,
        )

        rstart = int(time.time())
        await continue_request()
        rend = int(time.time())

        eaveLogger.info(
            f"Server Request End: {state.ctx.eave_request_id}: {scope['method']} {scope['path']}",
            state.ctx,
            { "request_duration": rend-rstart },
        )
