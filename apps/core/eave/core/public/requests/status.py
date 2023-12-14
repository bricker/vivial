import http
import json
from sqlalchemy import text
from starlette.requests import Request
from starlette.responses import Response
from eave.stdlib.endpoints import status_payload
from eave.stdlib.headers import MIME_TYPE_JSON


from eave.stdlib.http_endpoint import HTTPEndpoint
import eave.core.internal.database as eave_db
import eave.core.internal
from eave.stdlib.config import shared_config


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
        status_code = http.HTTPStatus.OK
        status = status_payload().dict()

        async with eave_db.async_session.begin() as db_session:
            result = await db_session.execute(text("SELECT 1"))
            rows = result.all()

        if len(rows) == 0:
            status_code = http.HTTPStatus.SERVICE_UNAVAILABLE
            status["status"] = "UNHEALTHY"

        content = json.dumps(status)
        return Response(status_code=status_code, content=content, media_type=MIME_TYPE_JSON)


class WarmupRequest(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        shared_config.preload()
        eave.core.internal.app_config.preload()
        return Response(status_code=http.HTTPStatus.OK, content="OK")


class StartRequest(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        return Response(status_code=http.HTTPStatus.OK, content="OK")


class StopRequest(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        return Response(status_code=http.HTTPStatus.OK, content="OK")
