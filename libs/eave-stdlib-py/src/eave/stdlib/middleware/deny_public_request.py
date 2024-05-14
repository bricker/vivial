from collections.abc import Awaitable, Callable

import asgiref.typing
from starlette.requests import Request

from eave.stdlib.logging import LogContext

from ..api_util import get_header_value
from ..exceptions import NotFoundError
from ..headers import EAVE_LB_HEADER
from .base import EaveASGIMiddleware


class DenyPublicRequestASGIMiddleware(EaveASGIMiddleware):
    async def process_request(
        self,
        scope: asgiref.typing.HTTPScope,
        receive: asgiref.typing.ASGIReceiveCallable,
        send: asgiref.typing.ASGISendCallable,
        request: Request,
        ctx: LogContext,
        continue_request: Callable[[], Awaitable[None]],
    ) -> None:
        # The EAVE_LB_HEADER header gets added onto the request at the load balancer.
        # Internal traffic isn't routed through the load balancer, so won't have this header.
        eave_lb_header = get_header_value(scope=scope, name=EAVE_LB_HEADER)

        if eave_lb_header:
            raise NotFoundError()

        await continue_request()
