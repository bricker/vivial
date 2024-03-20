from http import HTTPStatus

import aiohttp
from eave.stdlib.core_api.operations.status import Status

from eave.stdlib.headers import MIME_TYPE_JSON, MIME_TYPE_TEXT

from .base import BaseTestCase


class TestBodyParserMiddleware(BaseTestCase):
    async def test_body_parser_with_no_body(self) -> None:
        response = await self.make_request(
            method=Status.config.method,
            path=Status.config.path,
        )

        assert response.status_code == HTTPStatus.OK

    async def test_body_parser_with_json_body(self) -> None:
        response = await self.make_request(
            path=Status.config.path,
            payload=self.anydict(),
            headers={
                aiohttp.hdrs.CONTENT_TYPE: MIME_TYPE_JSON,
            },
        )

        assert response.status_code == HTTPStatus.OK

    async def test_body_parser_with_text_body(self) -> None:
        response = await self.make_request(
            path=Status.config.path,
            data=self.anystring(),
            headers={
                aiohttp.hdrs.CONTENT_TYPE: MIME_TYPE_TEXT,
            },
        )

        assert response.status_code == HTTPStatus.OK
