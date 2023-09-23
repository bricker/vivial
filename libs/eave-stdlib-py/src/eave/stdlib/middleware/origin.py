from asgiref.typing import ASGIReceiveCallable, ASGISendCallable, HTTPScope, Scope

from .base import EaveASGIMiddleware
from ..api_util import get_header_value
from ..headers import EAVE_ORIGIN_HEADER
from ..exceptions import MissingRequiredHeaderError
from ..eave_origins import EaveApp
from ..request_state import EaveRequestState


class OriginASGIMiddleware(EaveASGIMiddleware):
    async def __call__(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        if scope["type"] == "http":
            self._process_origin(scope=scope)

        await self.app(scope, receive, send)

    def _process_origin(self, scope: HTTPScope) -> None:
        eave_state = EaveRequestState.load(scope=scope)
        origin_header = get_header_value(scope=scope, name=EAVE_ORIGIN_HEADER)
        if not origin_header:
            if not self.endpoint_config.origin_required:
                return
            else:
                raise MissingRequiredHeaderError(EAVE_ORIGIN_HEADER)

        origin = EaveApp(value=origin_header)
        eave_state.ctx.eave_origin = str(origin)
