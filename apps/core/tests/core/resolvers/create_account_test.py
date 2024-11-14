from http import HTTPStatus

from ..base import BaseTestCase

day_seconds = 60 * 60 * 24


class TestCreateAccountMutation(BaseTestCase):
    async def test_create_account(self) -> None:
        vis_id = self.anyuuid()

        response = await self.httpclient.post(
            "/graphql",
            json={
                "query": self.load_graphql_query("createAccount"),
                "variables": {},
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json().get("data").get("planOuting").get("outing").get("id") is not None
