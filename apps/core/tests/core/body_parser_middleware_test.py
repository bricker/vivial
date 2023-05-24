from http import HTTPStatus

from .base import BaseTestCase


class TestBodyParserMiddleware(BaseTestCase):
    async def test_body_parser_with_no_body(self) -> None:
        response = await self.make_request(
            method="GET",
            path="/status",
        )

        assert response.status_code == HTTPStatus.OK

    async def test_body_parser_with_json_body(self) -> None:
        response = await self.make_request(
            path="/status",
            payload=self.anydict(),
            headers={
                "content-type": "application/json",
            },
        )

        assert response.status_code == HTTPStatus.OK

    async def test_body_parser_with_text_body(self) -> None:
        response = await self.make_request(
            path="/status",
            data=self.anystring(),
            headers={
                "content-type": "text/plain",
            },
        )

        assert response.status_code == HTTPStatus.OK
