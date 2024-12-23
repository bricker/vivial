import http
from typing import override

from asgiref.typing import HTTPScope
from starlette.requests import Request
from starlette.responses import Response

from eave.stdlib.headers import MIME_TYPE_JSON
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.status import status_payload


class StatusEndpoint(HTTPEndpoint):
    @override
    async def handle(self, request: Request, scope: HTTPScope) -> Response:
        status_code = http.HTTPStatus.OK
        content = status_payload().json()
        return Response(status_code=status_code, content=content, media_type=MIME_TYPE_JSON)
