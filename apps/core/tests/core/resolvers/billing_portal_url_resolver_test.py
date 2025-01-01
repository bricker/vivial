from eave.stdlib.config import SHARED_CONFIG

from ..base import BaseTestCase


class TestBillingPortalUrlQuery(BaseTestCase):
    async def test_get_billing_portal_url_with_customer_id_available(self) -> None:
        assert self.get_mock("stripe.billing_portal.Session.create_async").call_count == 0
        assert self.get_mock("stripe.billing_portal.Configuration.create_async").call_count == 0

        async with self.db_session.begin() as session:
            account = self.make_account(session)
            account.stripe_customer_id = self.anystr("stripe customer id")

        self.mock_stripe_billing_session.url = self.anyurl("billing portal url")

        response = await self.make_graphql_request(
            "billingPortalUrl",
            {},
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        assert result.data["viewer"]["__typename"] == "AuthenticatedViewerQueries"
        data = result.data["viewer"]["billingPortalUrl"]

        assert data == self.geturl("billing portal url")

        assert self.get_mock("stripe.billing_portal.Configuration.create_async").call_count == 1
        assert self.get_mock("stripe.billing_portal.Configuration.create_async").call_args_list[0].kwargs["features"]["invoice_history"]["enabled"] is False
        assert self.get_mock("stripe.billing_portal.Configuration.create_async").call_args_list[0].kwargs["features"]["customer_update"]["enabled"] is False
        assert self.get_mock("stripe.billing_portal.Configuration.create_async").call_args_list[0].kwargs["features"]["payment_method_update"]["enabled"] is True

        assert self.get_mock("stripe.billing_portal.Session.create_async").call_count == 1
        assert self.get_mock("stripe.billing_portal.Session.create_async").call_args_list[0].kwargs[
            "customer"
        ] == self.getstr("stripe customer id")
        assert (
            self.get_mock("stripe.billing_portal.Session.create_async").call_args_list[0].kwargs["return_url"]
            == f"{SHARED_CONFIG.eave_dashboard_base_url_public}/account"
        )
        assert (
            self.get_mock("stripe.billing_portal.Session.create_async").call_args_list[0].kwargs["configuration"]
            == self.mock_stripe_billing_configuration.id
        )

    async def test_get_billing_portal_url_without_customer_id_available(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            account.stripe_customer_id = None

        response = await self.make_graphql_request(
            "billingPortalUrl",
            {},
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        assert result.data["viewer"]["__typename"] == "AuthenticatedViewerQueries"
        data = result.data["viewer"]["billingPortalUrl"]

        assert data == SHARED_CONFIG.stripe_customer_portal_url

        assert self.get_mock("stripe.billing_portal.Configuration.create_async").call_count == 0
        assert self.get_mock("stripe.billing_portal.Session.create_async").call_count == 0
