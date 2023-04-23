from http import HTTPStatus
from typing import Any, Awaitable, Callable, List, Set
import fastapi
from starlette.middleware.base import BaseHTTPMiddleware
import eave.core.public.requests.util as request_util
import eave.stdlib.eave_origins as eave_origins
import eave.stdlib.core_api.headers as eave_headers
from . import EaveMiddleware
from eave.stdlib import logger

_BYPASS: Set[str] = set()

def add_bypass(path: str) -> None:
    global _BYPASS
    _BYPASS.add(path)

class OriginMiddleware(EaveMiddleware):
    async def dispatch(self, request: fastapi.Request, call_next: Callable[[fastapi.Request], Awaitable[fastapi.Response]]) -> fastapi.Response:
        global _BYPASS
        if request.url.path not in _BYPASS:
            origin_header = request.headers.get(eave_headers.EAVE_ORIGIN_HEADER)
            if not origin_header:
                logger.error("missing/empty eave origin header", extra=request_util.log_context(request))
                raise fastapi.HTTPException(HTTPStatus.BAD_REQUEST)

            try:
                origin = eave_origins.EaveOrigin(value=origin_header)
                request.state.eave_origin = origin
            except ValueError as e:
                logger.error("invalid eave origin", extra=request_util.log_context(request))
                raise fastapi.HTTPException(HTTPStatus.BAD_REQUEST) from e

        response = await call_next(request)
        return response

