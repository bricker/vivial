import eave.stdlib.eave_origins as eave_origins
import eave.stdlib.exceptions as eave_exceptions
import eave.stdlib.headers as eave_headers
from asgiref.typing import ASGIReceiveCallable, ASGISendCallable, HTTPScope, Scope
from eave.stdlib import api_util, logger

import eave.stdlib.lib.request_state as request_util

from eave.stdlib.middleware.base import EaveASGIMiddleware


class OriginASGIMiddleware(EaveASGIMiddleware):
    async def __call__(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        if scope["type"] == "http":
            self._process_origin(scope=scope)

        await self.app(scope, receive, send)

    @staticmethod
    def _process_origin(scope: HTTPScope) -> None:
        eave_state = request_util.get_eave_state(scope)

        origin_header = api_util.get_header_value(scope=scope, name=eave_headers.EAVE_ORIGIN_HEADER)
        if not origin_header:
            logger.error("missing/empty eave origin header", extra=eave_state.log_context)
            raise eave_exceptions.MissingRequiredHeaderError("eave-origin")

        try:
            origin = eave_origins.EaveOrigin(value=origin_header)
            eave_state.eave_origin = origin
        except ValueError as e:
            logger.error("invalid eave origin", exc_info=e, extra=eave_state.log_context)
            raise eave_exceptions.BadRequestError() from e
