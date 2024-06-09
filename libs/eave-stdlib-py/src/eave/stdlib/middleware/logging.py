import time
from collections.abc import Awaitable, Callable
from typing import cast

import asgiref.typing
from starlette.requests import Request

from eave.stdlib.api_util import get_headers
from eave.stdlib.typing import JsonObject

from ..logging import LOGGER, LogContext
from .base import EaveASGIMiddleware


class LoggingASGIMiddleware(EaveASGIMiddleware):
    async def process_request(
        self,
        scope: asgiref.typing.HTTPScope,
        receive: asgiref.typing.ASGIReceiveCallable,
        send: asgiref.typing.ASGISendCallable,
        request: Request,
        ctx: LogContext,
        continue_request: Callable[[], Awaitable[None]],
    ) -> None:
        LOGGER.info(
            f"Server Request Start: {ctx.eave_request_id}: {scope['method']} {scope['path']}",
            ctx,
        )

        # Add request headers to the log context.
        ctx["headers"] = cast(JsonObject, get_headers(scope=scope))

        rstart = int(time.time())
        await continue_request()
        rend = int(time.time())

        LOGGER.info(
            f"Server Request End: {ctx.eave_request_id}: {scope['method']} {scope['path']}",
            {"request_duration": rend - rstart},
            ctx,
        )
