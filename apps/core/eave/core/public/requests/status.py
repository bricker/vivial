import http
import json

from asgiref.typing import HTTPScope
from starlette.requests import Request
from starlette.responses import Response

from eave.stdlib.core_api.operations.status import status_payload
from eave.stdlib.headers import MIME_TYPE_JSON
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.logging import LogContext


class StatusEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        status_code = http.HTTPStatus.OK
        status = status_payload().dict()
        content = json.dumps(status)
        return Response(status_code=status_code, content=content, media_type=MIME_TYPE_JSON)


class HealthEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        return Response(status_code=http.HTTPStatus.OK, content="1")
