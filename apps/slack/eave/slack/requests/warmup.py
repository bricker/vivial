import http
from starlette.requests import Request
from starlette.responses import Response
from eave.stdlib.api_util import json_response
from eave.stdlib.config import shared_config
import eave.stdlib.cache as cache
from eave.stdlib.endpoints import status_payload
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.signing import preload_public_keys
from ..config import app_config
from eave.stdlib.logging import eaveLogger
import eave.stdlib.cache

class WarmupRequest(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        eaveLogger.info(
            "Received warmup request",
        )

        shared_config.preload()
        app_config.preload()
        preload_public_keys()

        try:
            # Lazily creates a Redis connection
            cache.client()
        except Exception:
            # If a Redis connection can't be established, it shouldn't prevent the app from warming up,
            # because currently Redis isn't technically required to run the app (cache requests fallback to API requests)
            eaveLogger.exception("Error connecting to redis")

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

class StatusRequest(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        return await self.get(request=request)

    async def delete(self, request: Request) -> Response:
        return await self.get(request=request)

    async def head(self, request: Request) -> Response:
        return await self.get(request=request)

    async def options(self, request: Request) -> Response:
        return await self.get(request=request)

    async def get(self, request: Request) -> Response:
        status = status_payload()
        if eave.stdlib.cache.initialized():
            try:
                await eave.stdlib.cache.client().ping()
            except Exception as e:
                eaveLogger.exception(e)
                status.status = "UNHEALTHY"

        return json_response(model=status)
