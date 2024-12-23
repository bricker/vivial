from dataclasses import dataclass
from typing import override

from aiohttp.hdrs import METH_DELETE, METH_GET, METH_PATCH, METH_POST, METH_PUT
from asgiref.typing import HTTPScope
from starlette.requests import Request
from starlette.responses import Response

from eave.stdlib.http_endpoint import HTTPEndpoint


@dataclass
class _Config:
    path: str
    method: str
    is_public: bool


class DummyEndpoint(HTTPEndpoint):
    pass


class EchoGetEndpoint(DummyEndpoint):
    config = _Config(
        path="/echo/get",
        method=METH_GET,
        is_public=True,
    )

    @override
    async def handle(self, request: Request, scope: HTTPScope) -> Response:
        body = await request.body()
        assert len(body) == 0

        qp = str(request.query_params)
        return Response(content=qp)


class EchoPostEndpoint(DummyEndpoint):
    config = _Config(
        path="/echo/post",
        method=METH_POST,
        is_public=True,
    )

    @override
    async def handle(self, request: Request, scope: HTTPScope) -> Response:
        body = await request.body()
        return Response(content=body)


class EchoPutEndpoint(DummyEndpoint):
    config = _Config(
        path="/echo/put",
        method=METH_PUT,
        is_public=True,
    )

    @override
    async def handle(self, request: Request, scope: HTTPScope) -> Response:
        body = await request.body()
        return Response(content=body)


class EchoPatchEndpoint(DummyEndpoint):
    config = _Config(
        path="/echo/patch",
        method=METH_PATCH,
        is_public=True,
    )

    @override
    async def handle(self, request: Request, scope: HTTPScope) -> Response:
        body = await request.body()
        return Response(content=body)


class DummyDeleteEndpoint(DummyEndpoint):
    config = _Config(
        path="/echo/delete",
        method=METH_DELETE,
        is_public=True,
    )

    @override
    async def handle(self, request: Request, scope: HTTPScope) -> Response:
        body = await request.body()
        assert len(body) == 0
        return Response()


class DummyInternalEndpoint(DummyEndpoint):
    config = _Config(
        path="/internal/get",
        method=METH_GET,
        is_public=False,
    )

    @override
    async def handle(self, request: Request, scope: HTTPScope) -> Response:
        return Response()
