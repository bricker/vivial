import http

from google.cloud import bigquery

from eave.stdlib.auth_cookies import EAVE_ACCESS_TOKEN_COOKIE_NAME, EAVE_ACCOUNT_ID_COOKIE_NAME
from eave.stdlib.config import SHARED_CONFIG

from .base import BaseTestCase

client = bigquery.Client(project=SHARED_CONFIG.google_cloud_project)


class TestMetabaseEmbeddingSSOEndpoints(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        async with self.db_session.begin() as s:
            self._account = await self.make_account(session=s)

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()

    async def test_metabase_auth_proxy(self) -> None:
        self.fail("need to mock the internal request to metabase backend")
        response = await self.make_request(
            path="/public/mb",
            cookies={
                EAVE_ACCOUNT_ID_COOKIE_NAME: str(self._account.id),
                EAVE_ACCESS_TOKEN_COOKIE_NAME: self._account.access_token,
            },
            payload={
                "return_to": self.anypath("return_to"),
            },
        )

        assert response.status_code == http.HTTPStatus.OK
