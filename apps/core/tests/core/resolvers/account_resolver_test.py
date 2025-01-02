from eave.stdlib.config import SHARED_CONFIG

from ..base import BaseTestCase


class TestGetViewerAccountQuery(BaseTestCase):
    async def test_get_viewer_account(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)

        response = await self.make_graphql_request(
            "getViewerAccount",
            {},
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        assert result.data["viewer"]["__typename"] == "AuthenticatedViewerQueries"
        data = result.data["viewer"]["account"]

        assert data["id"] == str(account.id)
        assert data["email"] == account.email
        assert data["stripeCustomerId"] == account.stripe_customer_id

    async def test_get_viewer_account_unauthenticated(self) -> None:
        response = await self.make_graphql_request(
            "getViewerAccount",
            {},
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        assert result.data["viewer"]["__typename"] == "UnauthenticatedViewer"
        assert "account" not in result.data["viewer"]
