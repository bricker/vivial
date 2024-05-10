from asgiref.typing import HTTPScope
from starlette.requests import Request
from starlette.responses import Response

from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.request_state import EaveRequestState


class NoopEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, state: EaveRequestState) -> Response:
        return Response()
