from asgiref.typing import HTTPScope
from eave.stdlib.headers import MIME_TYPE_JSON
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.logging import LogContext
from eave.stdlib.status import status_payload
from starlette.requests import Request
from starlette.responses import Response


import http


class StatusEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        status_code = http.HTTPStatus.OK
        content = status_payload().json()
        return Response(status_code=status_code, content=content, media_type=MIME_TYPE_JSON)
