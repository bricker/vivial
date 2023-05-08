from ..http_endpoint import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import Response

class NoopRequest(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        return Response()
