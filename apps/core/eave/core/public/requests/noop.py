from starlette.requests import Request
from starlette.responses import Response

from eave.stdlib.http_endpoint import HTTPEndpoint


class NoopRequest(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        return Response()
