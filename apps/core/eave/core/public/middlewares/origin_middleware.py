from typing import Set

import eave.core.public.requests.util as request_util
import eave.stdlib.core_api.headers as eave_headers
import eave.stdlib.eave_origins as eave_origins
import eave.stdlib.exceptions as eave_exceptions
from eave.stdlib import logger

from . import EaveASGIMiddleware, asgi_types

_BYPASS: Set[str] = set()


def add_bypass(path: str) -> None:
    global _BYPASS
    _BYPASS.add(path)


class OriginASGIMiddleware(EaveASGIMiddleware):
    async def process(
        self, scope: asgi_types.Scope, receive: asgi_types.ASGIReceiveCallable, send: asgi_types.ASGISendCallable
    ) -> None:
        if scope["type"] == "http" and scope["path"] not in _BYPASS:
            self._process_origin(scope=scope)

        await self.app(scope, receive, send)

    @staticmethod
    def _process_origin(scope: asgi_types.HTTPScope) -> None:
        origin_header = request_util.get_header_value(scope=scope, name=eave_headers.EAVE_ORIGIN_HEADER)
        if not origin_header:
            logger.error("missing/empty eave origin header", extra=request_util.log_context(scope=scope))
            raise eave_exceptions.MissingRequiredHeaderError("eave-origin")

        try:
            origin = eave_origins.EaveOrigin(value=origin_header)
            request_util.get_eave_state(scope=scope).eave_origin = origin
        except ValueError as e:
            logger.error("invalid eave origin", extra=request_util.log_context(scope=scope))
            raise eave_exceptions.BadRequestError()
