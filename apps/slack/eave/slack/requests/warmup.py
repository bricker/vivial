import http
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import Response
from eave.stdlib import cache, shared_config
from ..config import app_config
from eave.stdlib import eaveLogger


class WarmupRequest(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        eaveLogger.info(
            "Received warmup request",
        )

        shared_config.preload()
        app_config.preload()

        try:
            # Lazily creates a Redis connection
            cache.client()
        except Exception:
            # If a Redis connection can't be established, it shouldn't prevent the app from warming up,
            # because currently Redis isn't technically required to run the app (cache requests fallback to API requests)
            eaveLogger.exception("Error connecting to redis")

        return Response(status_code=http.HTTPStatus.OK, content="OK")
