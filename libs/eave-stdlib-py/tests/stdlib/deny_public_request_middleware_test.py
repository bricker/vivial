from http import HTTPStatus

import starlette.applications
from httpx import AsyncClient
from starlette.routing import Route

from eave.stdlib.middleware.deny_public_request import DenyPublicRequestASGIMiddleware

from .base import StdlibBaseTestCase
from .dummy_endpoints import DummyEndpoint, DummyInternalEndpoint


class TestDenyPublicRequestASGIMiddleware(StdlibBaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        endpoints: list[type[DummyEndpoint]] = [DummyInternalEndpoint]

        self.dummy_app = starlette.applications.Starlette(
            routes=[
                Route(methods=[e.config.method], path=e.config.path, endpoint=DenyPublicRequestASGIMiddleware(app=e))
                for e in endpoints
            ],
        )

        self.httpclient = AsyncClient(
            app=self.dummy_app,
            base_url="http://eave.tests",
        )

    async def test_internal_request_not_blocked_if_lb_header_not_set(self) -> None:
        response = await self.httpclient.request(
            method=DummyInternalEndpoint.config.method,
            url=DummyInternalEndpoint.config.path,
        )

        assert response.status_code == HTTPStatus.OK

    async def test_internal_request_blocked_if_lb_header_set(self) -> None:
        response = await self.httpclient.request(
            method=DummyInternalEndpoint.config.method,
            url=DummyInternalEndpoint.config.path,
            headers={
                "eave-lb": "1",
            },
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
