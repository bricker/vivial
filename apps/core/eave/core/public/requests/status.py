import http
import json
from typing import override

from asgiref.typing import HTTPScope
from eave.stdlib.request_state import EaveRequestState
from sqlalchemy import text
from starlette.requests import Request
from starlette.responses import Response

import eave.core.internal.database as eave_db
from eave.core.internal.config import CORE_API_APP_CONFIG
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.core_api.operations.status import status_payload
from eave.stdlib.headers import MIME_TYPE_JSON
from eave.stdlib.http_endpoint import HTTPEndpoint


class StatusEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, state: EaveRequestState) -> Response:
        status_code = http.HTTPStatus.OK
        status = status_payload().dict()
        content = json.dumps(status)
        return Response(status_code=status_code, content=content, media_type=MIME_TYPE_JSON)

class HealthEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, state: EaveRequestState) -> Response:
        return Response(status_code=http.HTTPStatus.OK, content="1")
