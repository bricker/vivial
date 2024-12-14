import http

from asgiref.typing import HTTPScope
from starlette.requests import Request
from starlette.responses import Response

from eave.stdlib.http_endpoint import HTTPEndpoint


class HealthEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope) -> Response:
        return Response(status_code=http.HTTPStatus.OK, content="1")
