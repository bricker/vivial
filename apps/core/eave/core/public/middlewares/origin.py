import eave.stdlib
import eave.stdlib.request_state
import eave.core.public
from asgiref.typing import ASGIReceiveCallable, ASGISendCallable, HTTPScope, Scope

from eave.stdlib.middleware.base import EaveASGIMiddleware


class OriginASGIMiddleware(EaveASGIMiddleware):
    async def __call__(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        if scope["type"] == "http":
            with self.auto_eave_state(scope=scope) as eave_state:
                self._process_origin(scope=scope, eave_state=eave_state)

        await self.app(scope, receive, send)

    @staticmethod
    def _process_origin(scope: HTTPScope, eave_state: eave.stdlib.request_state.EaveRequestState) -> None:
        origin_header = eave.stdlib.api_util.get_header_value(scope=scope, name=eave.stdlib.headers.EAVE_ORIGIN_HEADER)
        if not origin_header:
            raise eave.stdlib.exceptions.MissingRequiredHeaderError(eave.stdlib.headers.EAVE_ORIGIN_HEADER)

        try:
            origin = eave.stdlib.EaveOrigin(value=origin_header)
            eave_state.eave_origin = str(origin)
        except ValueError:
            raise eave.stdlib.exceptions.BadRequestError("invalid eave-origin")
