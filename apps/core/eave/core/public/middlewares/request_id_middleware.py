from typing import Any, Awaitable, Callable, List, Set
import uuid
import fastapi
from starlette.middleware.base import BaseHTTPMiddleware
from . import EaveMiddleware

class RequestIdMiddleware(EaveMiddleware):
    async def dispatch(self, request: fastapi.Request, call_next: Callable[[fastapi.Request], Awaitable[fastapi.Response]]) -> fastapi.Response:
        request.state.request_id = uuid.uuid4()
        response = await call_next(request)
        return response
