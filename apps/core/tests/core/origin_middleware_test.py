from http import HTTPStatus

from .base import BaseTestCase


class TestOriginMiddleware(BaseTestCase):
    async def test_origin_bypass(self) -> None:
        response = await self.make_request(
            method="GET",
            url="/status",
            headers={"eave-origin": None},
        )

        assert response.status_code == HTTPStatus.OK

    async def test_missing_origin_header(self) -> None:
        response = await self.make_request(
            url="/access_request",
            payload={
                "visitor_id": self.anystring("visitor_id"),
                "email": f"{self.anystring('email')}@example.com",
                "opaque_input": self.anystring("opaque_input"),
            },
            headers={
                "eave-origin": None,
            },
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST

    async def test_invalid_origin(self) -> None:
        response = await self.make_request(
            url="/access_request",
            payload={
                "visitor_id": self.anystring("visitor_id"),
                "email": f"{self.anystring('email')}@example.com",
                "opaque_input": self.anystring("opaque_input"),
            },
            headers={
                "eave-origin": "invalid",
            },
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
