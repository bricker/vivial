from typing import override

from asgiref.typing import HTTPScope
from starlette.requests import Request
from starlette.responses import Response

from eave.stdlib.http_endpoint import HTTPEndpoint


class NoopEndpoint(HTTPEndpoint):
    @override
    async def handle(self, request: Request, scope: HTTPScope) -> Response:
        return Response()
