import http
from http import HTTPStatus

from httpx import AsyncClient
from starlette.applications import Starlette
from starlette.routing import Route

from eave.stdlib.eave_origins import EaveApp
from eave.stdlib.middleware.origin import OriginASGIMiddleware

from .base import StdlibBaseTestCase
from .dummy_endpoints import EchoGetEndpoint


# TODO: Separate tests for testing response status codes. By default, the HTTP client used for tests raises app exceptions.
# https://github.com/encode/httpx/blob/a682f6f1c7f1c5e10c66ae5bef139aea37ef0c4e/httpx/_transports/asgi.py#L71
class TestOriginMiddleware(StdlibBaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        self.dummy_app = Starlette(
            routes=[
                Route(
                    methods=[EchoGetEndpoint.config.method],
                    path=f"{EchoGetEndpoint.config.path}/no-origin",
                    endpoint=EchoGetEndpoint,
                ),
                Route(
                    methods=[EchoGetEndpoint.config.method],
                    path=f"{EchoGetEndpoint.config.path}/origin-required",
                    endpoint=OriginASGIMiddleware(app=EchoGetEndpoint),
                ),
            ],
        )

        self.httpclient = AsyncClient(
            app=self.dummy_app,
            base_url="http://eave.tests",
        )

    async def test_origin_bypass(self) -> None:
        response = await self.httpclient.request(
            method=EchoGetEndpoint.config.method,
            url=f"{EchoGetEndpoint.config.path}/no-origin",
        )

        assert response.status_code == HTTPStatus.OK

    async def test_missing_origin_header_when_required(self) -> None:
        # FIXME: This does raise an error (MissingRequiredHeaderError), but it's caught by Starlette so not registered here
        # if using "assertRaises"
        response = await self.httpclient.request(
            method=EchoGetEndpoint.config.method,
            url=f"{EchoGetEndpoint.config.path}/origin-required",
        )

        assert response.status_code == http.HTTPStatus.BAD_REQUEST

    async def test_invalid_origin(self) -> None:
        response = await self.httpclient.request(
            method=EchoGetEndpoint.config.method,
            url=f"{EchoGetEndpoint.config.path}/origin-required",
            headers={
                "eave-origin": self.anystr("invalid origin"),
            },
        )

        assert response.status_code == http.HTTPStatus.BAD_REQUEST

    async def test_valid_origin(self) -> None:
        response = await self.httpclient.request(
            method=EchoGetEndpoint.config.method,
            url=f"{EchoGetEndpoint.config.path}/origin-required",
            headers={"eave-origin": EaveApp.eave_api},
        )

        assert response.status_code == http.HTTPStatus.OK
