from typing import Set

import eave.core.public.requests.util as request_util
import eave.stdlib.headers as eave_headers
import eave.stdlib.eave_origins as eave_origins
import eave.stdlib.exceptions as eave_exceptions
from eave.stdlib import logger

from . import EaveASGIMiddleware, asgi_types

_ROUTE_BYPASS: Set[str] = set()


def add_bypass(path: str) -> None:
    global _ROUTE_BYPASS
    _ROUTE_BYPASS.add(path)


class OriginASGIMiddleware(EaveASGIMiddleware):
    async def __call__(
        self, scope: asgi_types.Scope, receive: asgi_types.ASGIReceiveCallable, send: asgi_types.ASGISendCallable
    ) -> None:
        if scope["type"] == "http" and scope["path"] not in _ROUTE_BYPASS:
            self._process_origin(scope=scope)

        await self.app(scope, receive, send)

    @staticmethod
    def _process_origin(scope: asgi_types.HTTPScope) -> None:
        eave_state = request_util.get_eave_state(scope)

        origin_header = request_util.get_header_value(scope=scope, name=eave_headers.EAVE_ORIGIN_HEADER)
        if not origin_header:
            logger.error("missing/empty eave origin header", extra=eave_state.log_context)
            raise eave_exceptions.MissingRequiredHeaderError("eave-origin")

        try:
            origin = eave_origins.EaveOrigin(value=origin_header)
            eave_state.eave_origin = origin
        except ValueError as e:
            logger.error("invalid eave origin", exc_info=e, extra=eave_state.log_context)
            raise eave_exceptions.BadRequestError() from e
