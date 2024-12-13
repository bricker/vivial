from eave.core.orm.account import AccountOrm
from eave.core.orm.outing import OutingActivityOrm, OutingOrm
from eave.core.orm.stripe_payment_intent_reference import StripePaymentIntentReferenceOrm
from eave.core.shared.enums import ActivitySource

from ..base import BaseTestCase


class TestCreatePaymentIntentResolver(BaseTestCase):
    async def test_successful_create_payment_intent(self) -> None:
        async with self.db_session.begin() as session:
            assert await self.count(session, StripePaymentIntentReferenceOrm) == 0

            account = self.make_account(session)
            session.add(account)

            survey = self.make_survey(session, account)
            session.add(survey)

            outing = OutingOrm(
                account=account,
                survey=survey,
                visitor_id=self.anyuuid(),
            )
            session.add(outing)

            outing.activities.append(
                OutingActivityOrm(
                    outing=outing,
                    headcount=survey.headcount,
                    source=ActivitySource.EVENTBRITE,
                    source_id=self.anydigits(),
                    start_time_utc=self.anydatetime(future=True),
                    timezone=self.anytimezone(),
                )
            )

        assert account.stripe_customer_id is None
        assert self.get_mock("stripe.PaymentIntent.create_async").call_count == 0
        assert self.get_mock("stripe.Customer.create_async").call_count == 0
        assert self.get_mock("EventbriteClient.list_ticket_classes_for_sale_for_event").call_count == 0

        response = await self.make_graphql_request(
            "createPaymentIntent",
            {
                "input": {
                    "outingId": str(outing.id),
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["createPaymentIntent"]

        assert data["__typename"] == "CreatePaymentIntentSuccess"
        assert data["paymentIntent"]["id"] == self.getstr("stripe.PaymentIntent.id")
        assert data["paymentIntent"]["clientSecret"] == self.getstr("stripe.PaymentIntent.client_secret")

        async with self.db_session.begin() as session:
            assert await self.count(session, StripePaymentIntentReferenceOrm) == 1
            fetched_stripe_payment_intent_reference = await StripePaymentIntentReferenceOrm.get_one(
                session, account_id=account.id, stripe_payment_intent_id=self.getstr("stripe.PaymentIntent.id")
            )
            fetched_account = await AccountOrm.get_one(session, account.id)

        assert fetched_account.stripe_customer_id == self.getstr("stripe.Customer.id")
        assert fetched_stripe_payment_intent_reference.stripe_payment_intent_id == self.getstr(
            "stripe.PaymentIntent.id"
        )

        list_eventbrite_ticket_classes_mock = self.get_mock("EventbriteClient.list_ticket_classes_for_sale_for_event")
        assert list_eventbrite_ticket_classes_mock.call_count == 1

        create_payment_intent_mock = self.get_mock("stripe.PaymentIntent.create_async")
        assert create_payment_intent_mock.call_count == 1
        assert create_payment_intent_mock.call_args_list[0].kwargs["customer"] == fetched_account.stripe_customer_id
        assert create_payment_intent_mock.call_args_list[0].kwargs["receipt_email"] == fetched_account.email
        assert create_payment_intent_mock.call_args_list[0].kwargs["capture_method"] == "manual"
        assert create_payment_intent_mock.call_args_list[0].kwargs["amount"] == self.getint(
            "eventbrite.TicketClass.0.cost.value"
        ) + self.getint("eventbrite.TicketClass.0.fee.value") + self.getint("eventbrite.TicketClass.0.tax.value")

        create_customer_mock = self.get_mock("stripe.Customer.create_async")
        assert create_customer_mock.call_count == 1
        assert create_customer_mock.call_args_list[0].kwargs["metadata"]["vivial_account_id"] == str(account.id)

    async def test_create_payment_intent_creates_stripe_customer_account(self) -> None:
        async with self.db_session.begin() as session:
            assert await self.count(session, StripePaymentIntentReferenceOrm) == 0

            account = self.make_account(session)
            session.add(account)
            account.stripe_customer_id = self.anystr("stripe_customer_id")

            survey = self.make_survey(session, account)
            session.add(survey)

            outing = OutingOrm(
                account=account,
                survey=survey,
                visitor_id=self.anyuuid(),
            )
            session.add(outing)

        assert self.get_mock("stripe.Customer.create_async").call_count == 0

        response = await self.make_graphql_request(
            "createPaymentIntent",
            {
                "input": {
                    "outingId": str(outing.id),
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        assert result.data["viewer"]["createPaymentIntent"]["__typename"] == "CreatePaymentIntentSuccess"
        assert self.get_mock("stripe.Customer.create_async").call_count == 0

        async with self.db_session.begin() as session:
            assert await self.count(session, StripePaymentIntentReferenceOrm) == 1
            fetched_account = await AccountOrm.get_one(session, account.id)

        assert fetched_account.stripe_customer_id == self.getstr("stripe_customer_id")

    async def test_create_payment_intent_with_missing_client_secret(self) -> None:
        self.mock_stripe_payment_intent.client_secret = None

        async with self.db_session.begin() as session:
            assert await self.count(session, StripePaymentIntentReferenceOrm) == 0
            account = self.make_account(session)
            session.add(account)
            account.stripe_customer_id = self.anystr("sripe_customer_id")

            survey = self.make_survey(session, account)
            session.add(survey)

            outing = OutingOrm(
                account=account,
                survey=survey,
                visitor_id=self.anyuuid(),
            )
            session.add(outing)

        response = await self.make_graphql_request(
            "createPaymentIntent",
            {
                "input": {
                    "outingId": str(outing.id),
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        assert result.data["viewer"]["createPaymentIntent"]["__typename"] == "CreatePaymentIntentFailure"
        assert result.data["viewer"]["createPaymentIntent"]["failureReason"] == "PAYMENT_INTENT_FAILED"

        async with self.db_session.begin() as session:
            assert await self.count(session, StripePaymentIntentReferenceOrm) == 0
