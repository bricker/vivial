from http import HTTPStatus
import json
import unittest.mock

import aiohttp

from aiohttp.compression_utils import ZLibCompressor
from aiohttp.hdrs import METH_GET, METH_PATCH, METH_POST, METH_PUT
from eave.stdlib.core_api.operations.status import Status
from eave.stdlib.core_api.operations.team import GetMyTeamRequest
from eave.stdlib.headers import EAVE_LB_HEADER, ENCODING_GZIP, MIME_TYPE_JSON, MIME_TYPE_TEXT
from eave.stdlib.middleware.deny_public_request import DenyPublicRequestASGIMiddleware
from eave.stdlib.testing_util import UtilityBaseTestCase
from httpx import AsyncClient
from starlette.routing import Route
from .base import StdlibBaseTestCase
from .dummy_endpoints import DummyEndpoint, DummyInternalEndpoint
import starlette.applications

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
            }
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
