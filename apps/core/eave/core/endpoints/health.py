import http

from asgiref.typing import HTTPScope
from starlette.requests import Request
from starlette.responses import Response

from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.logging import LogContext


class HealthEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        return Response(status_code=http.HTTPStatus.OK, content="1")
