import http
from .base import BaseTestCase


class TestWarmupRequest(BaseTestCase):
    async def test_warmup_request(self) -> None:
        response = await self.httpclient.request(
            "GET",
            "/_ah/warmup",
        )

        assert response.status_code == http.HTTPStatus.OK
