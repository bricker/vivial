from asgiref.typing import ASGIReceiveCallable, ASGISendCallable, HTTPScope, Scope

from .base import EaveASGIMiddleware
from ..api_util import get_header_value
from ..headers import EAVE_ORIGIN_HEADER
from ..exceptions import MissingRequiredHeaderError
from ..eave_origins import EaveOrigin
from ..request_state import EaveRequestState


class OriginASGIMiddleware(EaveASGIMiddleware):
    async def __call__(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        if scope["type"] == "http":
            with self.auto_eave_state(scope=scope) as eave_state:
                self._process_origin(scope=scope, eave_state=eave_state)

        await self.app(scope, receive, send)

    @staticmethod
    def _process_origin(scope: HTTPScope, eave_state: EaveRequestState) -> None:
        origin_header = get_header_value(scope=scope, name=EAVE_ORIGIN_HEADER)
        if not origin_header:
            raise MissingRequiredHeaderError(EAVE_ORIGIN_HEADER)

        origin = EaveOrigin(value=origin_header)
        eave_state.eave_origin = str(origin)
