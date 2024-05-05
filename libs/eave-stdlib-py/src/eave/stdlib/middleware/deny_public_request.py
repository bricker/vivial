from typing import Awaitable, Callable
from starlette.requests import Request
import asgiref.typing
import starlette.types

from eave.stdlib.core_api.operations import EndpointConfiguration

from ..api_util import get_header_value
from ..eave_origins import EaveApp
from ..exceptions import InvalidOriginError, MissingRequiredHeaderError, NotFoundError
from ..headers import EAVE_LB_HEADER, EAVE_ORIGIN_HEADER
from ..request_state import EaveRequestState
from .base import EaveASGIMiddleware


class DenyPublicRequestASGIMiddleware(EaveASGIMiddleware):
    async def process_request(
        self,
        scope: asgiref.typing.HTTPScope,
        receive: asgiref.typing.ASGIReceiveCallable,
        send: asgiref.typing.ASGISendCallable,
        request: Request,
        state: EaveRequestState,
        continue_request: Callable[[], Awaitable[None]],
    ) -> None:
        # The EAVE_LB_HEADER header gets added onto the request at the load balancer.
        # Internal traffic isn't routed through the load balancer, so won't have this header.
        eave_lb_header = get_header_value(scope=scope, name=EAVE_LB_HEADER)

        if eave_lb_header:
            raise NotFoundError()

        await continue_request()
