import os
from http import HTTPStatus

from .base import BaseTestCase


class TestStatusEndpoint(BaseTestCase):
    async def test_status_endpoint(self) -> None:
        os.environ["GAE_SERVICE"] = self.anystring("gaeservice")
        os.environ["GAE_VERSION"] = self.anystring("gaeversion")

        response = await self.httpclient.get("/status")
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            "status": "OK",
            "service": self.anystring("gaeservice"),
            "version": self.anystring("gaeversion"),
        }
