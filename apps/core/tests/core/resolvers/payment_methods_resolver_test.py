import stripe

from ..base import BaseTestCase

day_seconds = 60 * 60 * 24


class TestPaymentMethodsResolvers(BaseTestCase):
    async def test_payment_methods_not_empty(self) -> None:
        self.mock_stripe_customer_payment_methods.data = [
            stripe.PaymentMethod(
                id=self.anystr("payment method id"),
            ),
        ]

        setattr(
            self.mock_stripe_customer_payment_methods.data[0],
            "card",
            stripe.Card(
                brand="visa",
                last4=self.anydigits(length=4),
                exp_month=self.anyint(min=1, max=12),
                exp_year=self.anyint(min=2020, max=2100),
            ),
        )

        async with self.db_session.begin() as session:
            account = self.make_account(session)
            account.stripe_customer_id = self.anystr("stripe customer id")

        response = await self.make_graphql_request("listPaymentMethods", {}, account_id=account.id)

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        assert self.get_mock("stripe.Customer.list_payment_methods_async").call_count == 1
        assert self.get_mock("stripe.Customer.list_payment_methods_async").call_args_list[0].kwargs[
            "customer"
        ] == self.getstr("stripe customer id")

        data = result.data["viewer"]["paymentMethods"]
        assert len(data) == 1
        assert data[0]["id"] == self.getstr("payment method id")

    async def test_payment_methods_empty(self) -> None:
        self.mock_stripe_customer_payment_methods.data = []

        async with self.db_session.begin() as session:
            account = self.make_account(session)
            account.stripe_customer_id = self.anystr("stripe customer id")

        response = await self.make_graphql_request("listPaymentMethods", {}, account_id=account.id)

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        assert self.get_mock("stripe.Customer.list_payment_methods_async").call_count == 1
        assert self.get_mock("stripe.Customer.list_payment_methods_async").call_args_list[0].kwargs[
            "customer"
        ] == self.getstr("stripe customer id")

        data = result.data["viewer"]["paymentMethods"]
        assert len(data) == 0

    async def test_payment_methods_no_customer_id(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            account.stripe_customer_id = None

        response = await self.make_graphql_request("listPaymentMethods", {}, account_id=account.id)

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        assert self.get_mock("stripe.Customer.list_payment_methods_async").call_count == 0

        data = result.data["viewer"]["paymentMethods"]
        assert len(data) == 0

    async def test_payment_methods_invalid_account_id(self) -> None:
        async with self.db_session.begin() as session:
            self.make_account(session)

        response = await self.make_graphql_request("listPaymentMethods", {}, account_id=self.anyuuid())

        result = self.parse_graphql_response(response)
        assert not result.data
        assert result.errors and len(result.errors) == 1

        assert self.get_mock("stripe.Customer.list_payment_methods_async").call_count == 0

    async def test_payment_methods_unauthed(self) -> None:
        response = await self.make_graphql_request(
            "listPaymentMethods",
            {},
            account_id=None,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        assert self.get_mock("stripe.Customer.list_payment_methods_async").call_count == 0
        assert "paymentMethods" not in result.data["viewer"]
        assert result.data["viewer"]["authFailureReason"] == "ACCESS_TOKEN_INVALID"
