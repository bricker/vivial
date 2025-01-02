import unittest.mock
from typing import Any, override

import stripe

from eave.stdlib.test_helpers.mocking_mixin import MockingMixin
from eave.stdlib.test_helpers.random_data_mixin import RandomDataMixin


class StripeMocksMixin(MockingMixin, RandomDataMixin):
    mock_stripe_payment_intent: stripe.PaymentIntent  # pyright: ignore [reportUninitializedInstanceVariable]
    mock_stripe_customer: stripe.Customer  # pyright: ignore [reportUninitializedInstanceVariable]
    mock_stripe_customer_session: stripe.CustomerSession  # pyright: ignore [reportUninitializedInstanceVariable]
    mock_stripe_customer_payment_methods: stripe.ListObject[stripe.PaymentMethod]  # pyright: ignore [reportUninitializedInstanceVariable]
    mock_stripe_billing_session: stripe.billing_portal.Session  # pyright: ignore [reportUninitializedInstanceVariable]
    mock_stripe_billing_configuration: stripe.billing_portal.Configuration  # pyright: ignore [reportUninitializedInstanceVariable]

    @override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self._add_stripe_client_mocks()

    def _add_stripe_client_mocks(self) -> None:
        mock_stripe_payment_intent = stripe.PaymentIntent(
            id=self.anystr("stripe.PaymentIntent.id"),
        )
        mock_stripe_payment_intent.client_secret = self.anystr("stripe.PaymentIntent.client_secret")
        mock_stripe_payment_intent.status = "requires_capture"
        self.mock_stripe_payment_intent = mock_stripe_payment_intent

        async def _mock_payment_intent_create_async(**kwargs: Any) -> stripe.PaymentIntent:
            return self.mock_stripe_payment_intent

        self.patch(
            name="stripe.PaymentIntent.create_async",
            patch=unittest.mock.patch("stripe.PaymentIntent.create_async"),
            side_effect=_mock_payment_intent_create_async,
        )

        async def _mock_payment_intent_retrieve_async(**kwargs: Any) -> stripe.PaymentIntent:
            return self.mock_stripe_payment_intent

        self.patch(
            name="stripe.PaymentIntent.retrieve_async",
            patch=unittest.mock.patch("stripe.PaymentIntent.retrieve_async"),
            side_effect=_mock_payment_intent_retrieve_async,
        )

        self.mock_stripe_customer = stripe.Customer(
            id=self.anystr("stripe.Customer.id"),
        )

        async def _mock_customer_create_async(**kwargs: Any) -> stripe.Customer:
            return self.mock_stripe_customer

        self.patch(
            name="stripe.Customer.create_async",
            patch=unittest.mock.patch("stripe.Customer.create_async"),
            side_effect=_mock_customer_create_async,
        )

        _lo = stripe.ListObject()
        _lo.data = [stripe.PaymentMethod(id=self.anystr())]
        self.mock_stripe_customer_payment_methods = _lo

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

        async def _mock_customer_list_payment_methods(
            *args: Any, **kwargs: Any
        ) -> stripe.ListObject[stripe.PaymentMethod]:
            return self.mock_stripe_customer_payment_methods

        self.patch(
            name="stripe.Customer.list_payment_methods_async",
            patch=unittest.mock.patch("stripe.Customer.list_payment_methods_async"),
            side_effect=_mock_customer_list_payment_methods,
        )

        self.mock_stripe_customer_session = stripe.CustomerSession()
        self.mock_stripe_customer_session.client_secret = self.anystr("stripe.CustomerSession.client_secret")

        async def _mock_customer_session_create_async(**kwargs: Any) -> stripe.CustomerSession:
            return self.mock_stripe_customer_session

        self.patch(
            name="stripe.CustomerSession.create_async",
            patch=unittest.mock.patch("stripe.CustomerSession.create_async"),
            side_effect=_mock_customer_session_create_async,
        )

        self.mock_stripe_billing_configuration = stripe.billing_portal.Configuration()
        self.mock_stripe_billing_configuration.id = self.anystr()

        async def _mock_billing_configuration_create_async(**kwargs: Any) -> stripe.billing_portal.Configuration:
            return self.mock_stripe_billing_configuration

        self.patch(
            name="stripe.billing_portal.Configuration.create_async",
            patch=unittest.mock.patch("stripe.billing_portal.Configuration.create_async"),
            side_effect=_mock_billing_configuration_create_async,
        )

        self.mock_stripe_billing_session = stripe.billing_portal.Session()
        self.mock_stripe_billing_session.url = self.anyurl()

        async def _mock_billing_session_create_async(**kwargs: Any) -> stripe.billing_portal.Session:
            return self.mock_stripe_billing_session

        self.patch(
            name="stripe.billing_portal.Session.create_async",
            patch=unittest.mock.patch("stripe.billing_portal.Session.create_async"),
            side_effect=_mock_billing_session_create_async,
        )
