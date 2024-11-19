from asgiref.typing import HTTPScope
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.logging import LogContext
from starlette.requests import Request
from starlette.responses import Response


class NoopEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        return Response()
