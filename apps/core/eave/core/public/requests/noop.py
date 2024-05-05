from typing import override
from asgiref.typing import HTTPScope
from eave.stdlib.request_state import EaveRequestState
from starlette.requests import Request
from starlette.responses import Response

from eave.stdlib.http_endpoint import HTTPEndpoint


class NoopEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, state: EaveRequestState) -> Response:
        return Response()
