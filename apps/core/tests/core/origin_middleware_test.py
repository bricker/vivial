from http import HTTPStatus

from .base import BaseTestCase


class TestOriginMiddleware(BaseTestCase):
    async def test_origin_bypass(self) -> None:
        response = await self.make_request(
            method="GET",
            path="/status",
            headers={"eave-origin": None},
        )

        assert response.status_code == HTTPStatus.OK

    async def test_missing_origin_header(self) -> None:
        response = await self.make_request(
            path="/integrations/slack/query",
            headers={
                "eave-origin": None,
            },
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST

    async def test_invalid_origin(self) -> None:
        response = await self.make_request(
            path="/integrations/slack/query",
            headers={
                "eave-origin": "invalid",
            },
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
