from collections.abc import Awaitable, Callable

import asgiref.typing
from starlette.requests import Request

from ..api_util import get_header_value
from ..eave_origins import EaveApp
from ..exceptions import InvalidOriginError, MissingRequiredHeaderError
from ..headers import EAVE_ORIGIN_HEADER
from ..request_state import EaveRequestState
from .base import EaveASGIMiddleware


class OriginASGIMiddleware(EaveASGIMiddleware):
    async def process_request(
        self,
        scope: asgiref.typing.HTTPScope,
        receive: asgiref.typing.ASGIReceiveCallable,
        send: asgiref.typing.ASGISendCallable,
        request: Request,
        state: EaveRequestState,
        continue_request: Callable[[], Awaitable[None]],
    ) -> None:
        origin_header = get_header_value(scope=scope, name=EAVE_ORIGIN_HEADER)
        if not origin_header:
            raise MissingRequiredHeaderError(EAVE_ORIGIN_HEADER)

        try:
            origin = EaveApp(value=origin_header)
            state.ctx.eave_origin = str(origin)
        except ValueError:
            raise InvalidOriginError()

        await continue_request()
