import http
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import Response
from eave.stdlib import shared_config
from ..config import app_config
from eave.stdlib import eaveLogger


class WarmupRequest(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        eaveLogger.info(
            "Received warmup request",
        )

        shared_config.preload()
        app_config.preload()
        return Response(status_code=http.HTTPStatus.OK, content="OK")
