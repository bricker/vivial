from typing import Any, Awaitable, Callable, List, Set
import fastapi
from starlette.middleware.base import BaseHTTPMiddleware
import eave.core.public.requests.util as request_util

_BYPASS: Set[str] = set()

def add_bypass(path: str) -> None:
    global _BYPASS
    _BYPASS.add(path)

class ValidateSignatureMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: fastapi.Request, call_next: Callable[[fastapi.Request], Awaitable[fastapi.Response]]) -> fastapi.Response:
        global _BYPASS
        if request.url.path not in _BYPASS:
            await request_util.validate_signature_or_fail(request=request)

        response = await call_next(request)
        return response
