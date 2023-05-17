import http
import json
from sqlalchemy import text
from starlette.requests import Request
from starlette.responses import Response

from ..http_endpoint import HTTPEndpoint
from eave.stdlib.api_util import status_payload
import eave.core.internal.database as eave_db
import eave.core.internal
import eave.core.public.request_state
from eave.stdlib import logger
import eave.stdlib


class StatusRequest(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        eave_state = eave.core.public.request_state.get_eave_state(request=request)
        status_code = http.HTTPStatus.OK

        status = status_payload().dict()

        async with eave_db.async_session.begin() as db_session:
            try:
                await db_session.execute(text("SELECT 1"))
            except Exception as e:
                logger.critical("Error connecting to database.", exc_info=e, extra=eave_state.log_context)
                status["status"] = "UNHEALTHY"
                status_code = http.HTTPStatus.SERVICE_UNAVAILABLE

        content = json.dumps(status)
        return Response(status_code=status_code, content=content, media_type="application/json")


class WarmupRequest(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        eave.stdlib.shared_config.preload()
        eave.core.internal.app_config.preload()
        return Response(status_code=http.HTTPStatus.OK, content="OK")
