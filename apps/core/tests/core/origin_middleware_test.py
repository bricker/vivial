from http import HTTPStatus
import http

import eave.stdlib.exceptions

from .base import BaseTestCase


# TODO: Separate tests for testing response status codes. By default, the HTTP client used for tests raises app exceptions.
# https://github.com/encode/httpx/blob/a682f6f1c7f1c5e10c66ae5bef139aea37ef0c4e/httpx/_transports/asgi.py#L71
class TestOriginMiddleware(BaseTestCase):
    async def test_origin_bypass(self) -> None:
        response = await self.make_request(
            method="GET",
            path="/status",
            headers={"eave-origin": None},
        )

        assert response.status_code == HTTPStatus.OK

    async def test_missing_origin_header(self) -> None:
        # FIXME: This does raise an error (MissingRequiredHeaderError), but it's caught by Starlette so not registered here
        # if using "assertRaises"
        response = await self.make_request(
            path="/integrations/slack/query",
            headers={
                "eave-origin": None,
            },
        )
        assert response.status_code == http.HTTPStatus.BAD_REQUEST
        assert response.text == "eave-origin"

    async def test_invalid_origin(self) -> None:
        with self.assertRaises(ValueError):
            await self.make_request(
                path="/integrations/slack/query",
                headers={
                    "eave-origin": "invalid",
                },
            )
