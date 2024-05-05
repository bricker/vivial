from http import HTTPStatus
import json
import unittest.mock

import aiohttp

from aiohttp.compression_utils import ZLibCompressor
from aiohttp.hdrs import METH_GET, METH_PATCH, METH_POST, METH_PUT
from eave.stdlib.core_api.operations.status import Status
from eave.stdlib.headers import ENCODING_GZIP, MIME_TYPE_JSON, MIME_TYPE_TEXT
from eave.stdlib.middleware.read_body import ReadBodyASGIMiddleware
from eave.stdlib.testing_util import UtilityBaseTestCase
from httpx import AsyncClient
import starlette.applications
from starlette.routing import Route

from .dummy_endpoints import DummyEndpoint, EchoGetEndpoint, EchoPatchEndpoint, EchoPostEndpoint, EchoPutEndpoint
from .base import StdlibBaseTestCase

huge_payload = json.dumps({
    "a": "b" * (pow(10, 6) * 2) # 2mb worth of "b"
})

class TestReadBodyASGIMiddleware(StdlibBaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        endpoints: list[type[DummyEndpoint]] = [EchoGetEndpoint, EchoPostEndpoint, EchoPatchEndpoint, EchoPutEndpoint]

        self.dummy_app = starlette.applications.Starlette(
            routes=[
                Route(methods=[e.config.method], path=e.config.path, endpoint=ReadBodyASGIMiddleware(app=e))
                for e in endpoints
            ],
        )

        self.httpclient = AsyncClient(
            app=self.dummy_app,
            base_url="http://eave.tests",
        )



    async def test_body_reader_with_valid_post_request(self) -> None:
        body = self.anyjson()

        response = await self.httpclient.request(
            method=EchoPostEndpoint.config.method,
            url=EchoPostEndpoint.config.path,
            content=body,
        )

        assert response.status_code == HTTPStatus.OK

    async def test_body_reader_with_valid_post_request_without_body(self) -> None:
        response = await self.httpclient.request(
            method=EchoPostEndpoint.config.method,
            url=EchoPostEndpoint.config.path,
            content=""
        )

        assert response.status_code == HTTPStatus.OK

    async def test_body_reader_with_valid_put_request(self) -> None:
        body = self.anyjson()

        response = await self.httpclient.request(
            method=EchoPutEndpoint.config.method,
            url=EchoPutEndpoint.config.path,
            content=body,
        )

        assert response.status_code == HTTPStatus.OK

    async def test_body_reader_with_valid_patch_request(self) -> None:
        body = self.anyjson()

        response = await self.httpclient.request(
            method=EchoPatchEndpoint.config.method,
            url=EchoPatchEndpoint.config.path,
            content=body,
        )

        assert response.status_code == HTTPStatus.OK

    async def test_body_reader_with_get_request_with_body(self) -> None:
        body = self.anyjson()

        response = await self.httpclient.request(
            method=EchoGetEndpoint.config.method,
            url=EchoGetEndpoint.config.path,
            content=body,
        )

        # The body should have been dropped.
        assert response.status_code == HTTPStatus.OK

    async def test_body_reader_with_get_request_without_body(self) -> None:
        response = await self.httpclient.request(
            method=EchoGetEndpoint.config.method,
            url=EchoGetEndpoint.config.path,
        )

        assert response.status_code == HTTPStatus.OK

    async def test_body_reader_with_too_large_body(self) -> None:
        response = await self.httpclient.request(
            method=EchoPostEndpoint.config.method,
            url=EchoPostEndpoint.config.path,
            content=huge_payload,
        )

        assert response.status_code == HTTPStatus.REQUEST_ENTITY_TOO_LARGE

    async def test_body_reader_with_too_large_content_length_header(self) -> None:
        body = self.anyjson()

        response = await self.httpclient.request(
            method=EchoPostEndpoint.config.method,
            url=EchoPostEndpoint.config.path,
            headers={
                aiohttp.hdrs.CONTENT_LENGTH: str(len(huge_payload))
            },
            content=body,
        )

        assert response.status_code == HTTPStatus.REQUEST_ENTITY_TOO_LARGE

    async def test_body_reader_with_mismatched_content_length_header(self) -> None:
        body = self.anyjson()

        response = await self.httpclient.request(
            method=EchoPostEndpoint.config.method,
            url=EchoPostEndpoint.config.path,
            headers={
                aiohttp.hdrs.CONTENT_LENGTH: str(len(body) + 100)
            },
            content=body,
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST

    async def test_body_reader_with_missing_content_length_header(self) -> None:
        body = self.anyjson()

        response = await self.httpclient.request(
            method=EchoPostEndpoint.config.method,
            url=EchoPostEndpoint.config.path,
            headers={
                aiohttp.hdrs.CONTENT_LENGTH: "",
            },
            content=body,
        )

        assert response.status_code == HTTPStatus.LENGTH_REQUIRED

    async def test_body_reader_with_gzip_body(self) -> None:
        body = self.anyjson()
        compressed_body = await ZLibCompressor(encoding=ENCODING_GZIP).compress(body.encode())

        response = await self.httpclient.request(
            method=EchoPostEndpoint.config.method,
            url=EchoPostEndpoint.config.path,
            headers={
                aiohttp.hdrs.CONTENT_ENCODING: ENCODING_GZIP,
            },
            content=compressed_body,
        )

        assert response.status_code == HTTPStatus.OK
