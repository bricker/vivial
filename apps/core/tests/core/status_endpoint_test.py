from http import HTTPStatus

from .base import BaseTestCase


class TestStatusEndpoint(BaseTestCase):
    async def test_status_endpoint(self) -> None:
        self.patch_env(
            values={
                "GAE_SERVICE": self.anystr("gaeservice"),
                "GAE_VERSION": self.anystr("gaeversion"),
                "GAE_RELEASE_DATE": self.anystr("gaereleasedate"),
            }
        )

        response = await self.httpclient.get("/status")
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            "status": "OK",
            "service": self.getstr("gaeservice"),
            "version": self.getstr("gaeversion"),
            "release_date": self.getstr("gaereleasedate"),
        }
