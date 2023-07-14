import http
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import Response
from eave.stdlib.config import shared_config
from eave.stdlib.signing import preload_public_keys
from ..config import app_config
from eave.stdlib.logging import eaveLogger


class WarmupRequest(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        eaveLogger.info(
            "Received warmup request",
        )

        shared_config.preload()
        app_config.preload()
        preload_public_keys()

        return Response(status_code=http.HTTPStatus.OK, content="OK")


class StartRequest(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        eaveLogger.info(
            "Received start request",
        )

        return Response(status_code=http.HTTPStatus.OK, content="OK")


class StopRequest(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        eaveLogger.info(
            "Received stop request",
        )

        return Response(status_code=http.HTTPStatus.OK, content="OK")
