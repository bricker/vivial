from uuid import UUID

from eave.core.orm.account import AccountOrm
from eave.core.orm.booking import BookingOrm
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.orm.stripe_payment_intent_reference import StripePaymentIntentReferenceOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.shared.enums import BookingState, OutingBudget
from eave.stdlib.eventbrite.models.shared import CurrencyCost
from eave.stdlib.eventbrite.models.ticket_class import TicketClass
from eave.stdlib.time import ONE_YEAR_IN_SECONDS

from ..base import BaseTestCase


class TestInitiateBookingResolver(BaseTestCase):
    async def test_valid_initiate_booking(self) -> None:
        assert self.get_mock("stripe.PaymentIntent.create_async").call_count == 0
        assert self.get_mock("stripe.Customer.create_async").call_count == 0
        assert self.get_mock("stripe.CustomerSession.create_async").call_count == 0

        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 0
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            survey.budget = OutingBudget.EXPENSIVE
            outing = self.make_outing(session, account, survey)

        self.set_mock_eventbrite_ticket_class_batch(max_cost_cents=survey.budget.upper_limit_cents)

        self.mock_stripe_payment_intent.amount = self.get_mock_eventbrite_ticket_class_batch_cost() * survey.headcount

        response = await self.make_graphql_request(
            "initiateBooking",
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

        data = result.data["viewer"]["initiateBooking"]
        assert data["__typename"] == "InitiateBookingSuccess"

        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 1
            booking = await BookingOrm.get_one(session, UUID(data["booking"]["id"]))

        assert len(booking.reservations) == 1
        assert booking.reservations[0].source_id == outing.reservations[0].source_id

        assert len(booking.activities) == 1
        assert booking.activities[0].source_id == outing.activities[0].source_id

        assert booking.reserver_details is None
        assert booking.state == BookingState.INITIATED

        assert booking.stripe_payment_intent_reference is not None

        payment_intent = data["paymentIntent"]
        assert payment_intent is not None
        assert payment_intent["id"] == self.mock_stripe_payment_intent.id
        assert payment_intent["clientSecret"] == self.mock_stripe_payment_intent.client_secret

        customer_session = data["customerSession"]
        assert customer_session is not None
        assert customer_session["clientSecret"] == self.mock_stripe_customer_session.client_secret

        assert self.get_mock("stripe.PaymentIntent.create_async").call_count == 1
        assert self.get_mock("stripe.Customer.create_async").call_count == 1
        assert self.get_mock("stripe.CustomerSession.create_async").call_count == 1
        assert self.get_mock("SendGridAPIClient.send").call_count == 0

    async def test_create_booking_free(self) -> None:
        assert self.get_mock("stripe.PaymentIntent.create_async").call_count == 0
        assert self.get_mock("stripe.Customer.create_async").call_count == 0
        assert self.get_mock("stripe.CustomerSession.create_async").call_count == 0

        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 0
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            outing = self.make_outing(session, account, survey)

        self.mock_eventbrite_ticket_class_batch = []

        response = await self.make_graphql_request(
            "initiateBooking",
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

        data = result.data["viewer"]["initiateBooking"]
        assert data["__typename"] == "InitiateBookingSuccess"

        assert data["paymentIntent"] is None
        assert data["customerSession"] is None

        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 1

        assert self.get_mock("stripe.PaymentIntent.create_async").call_count == 0
        assert self.get_mock("stripe.Customer.create_async").call_count == 0
        assert self.get_mock("stripe.CustomerSession.create_async").call_count == 0
        assert self.get_mock("SendGridAPIClient.send").call_count == 0

    async def test_create_booking_from_expired_outing_fails(self) -> None:
        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 0

            account = self.make_account(session)
            survey = SurveyOrm(
                session,
                account=account,
                visitor_id=self.anystr(),
                start_time_utc=self.anydatetime(past=True),
                timezone=self.anytimezone(),
                search_area_ids=[SearchRegionOrm.all()[0].id],
                budget=OutingBudget.INEXPENSIVE,
                headcount=self.anyint(min=1, max=2),
            )

            outing = self.make_outing(session, account, survey)

        response = await self.make_graphql_request(
            "initiateBooking",
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

        data = result.data["viewer"]["initiateBooking"]
        assert "booking" not in data
        assert data["failureReason"] == "START_TIME_TOO_SOON"

        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 0

        assert self.get_mock("SendGridAPIClient.send").call_count == 0

    async def test_create_booking_from_outing_too_far_future_fails(self) -> None:
        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 0

            account = self.make_account(session)
            survey = SurveyOrm(
                session,
                account=account,
                visitor_id=self.anystr(),
                start_time_utc=self.anydatetime(offset=ONE_YEAR_IN_SECONDS),
                timezone=self.anytimezone(),
                search_area_ids=[SearchRegionOrm.all()[0].id],
                budget=OutingBudget.INEXPENSIVE,
                headcount=self.anyint(min=1, max=2),
            )

            outing = self.make_outing(session, account, survey)

        response = await self.make_graphql_request(
            "initiateBooking",
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

        data = result.data["viewer"]["initiateBooking"]
        assert "booking" not in data
        assert data["failureReason"] == "START_TIME_TOO_LATE"

        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 0

        assert self.get_mock("SendGridAPIClient.send").call_count == 0

    async def test_successful_create_payment_intent(self) -> None:
        assert self.get_mock("stripe.PaymentIntent.create_async").call_count == 0
        assert self.get_mock("stripe.Customer.create_async").call_count == 0
        assert self.get_mock("stripe.CustomerSession.create_async").call_count == 0
        assert self.get_mock("EventbriteClient.list_ticket_classes_for_sale_for_event").call_count == 0

        async with self.db_session.begin() as session:
            assert await self.count(session, StripePaymentIntentReferenceOrm) == 0

            account = self.make_account(session)
            survey = self.make_survey(session, account)
            outing = self.make_outing(session, account, survey)

        assert account.stripe_customer_id is None

        self.mock_eventbrite_ticket_class_batch = [
            TicketClass(
                id=self.anydigits(),
                cost=CurrencyCost(
                    currency="usd",
                    display=self.anystr(),
                    major_value=self.anystr(),
                    value=self.anyint(max=survey.budget.upper_limit_cents),
                ),
                fee=CurrencyCost(
                    currency="usd",
                    display=self.anystr(),
                    major_value=self.anystr(),
                    value=0,
                ),
                tax=CurrencyCost(
                    currency="usd",
                    display=self.anystr(),
                    major_value=self.anystr(),
                    value=0,
                ),
            )
        ]

        response = await self.make_graphql_request(
            "initiateBooking",
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

        data = result.data["viewer"]["initiateBooking"]

        assert data["__typename"] == "InitiateBookingSuccess"
        assert data["paymentIntent"]["id"] == self.mock_stripe_payment_intent.id
        assert data["paymentIntent"]["clientSecret"] == self.mock_stripe_payment_intent.client_secret

        assert data["customerSession"]["clientSecret"] == self.mock_stripe_customer_session.client_secret

        async with self.db_session.begin() as session:
            assert await self.count(session, StripePaymentIntentReferenceOrm) == 1
            fetched_stripe_payment_intent_reference = await StripePaymentIntentReferenceOrm.get_one(
                session, account_id=account.id, stripe_payment_intent_id=self.mock_stripe_payment_intent.id
            )
            fetched_account = await AccountOrm.get_one(session, account.id)

        assert fetched_account.stripe_customer_id == self.mock_stripe_customer.id
        assert fetched_stripe_payment_intent_reference.stripe_payment_intent_id == self.mock_stripe_payment_intent.id

        list_eventbrite_ticket_classes_mock = self.get_mock("EventbriteClient.list_ticket_classes_for_sale_for_event")
        assert list_eventbrite_ticket_classes_mock.call_count == 1

        create_payment_intent_mock = self.get_mock("stripe.PaymentIntent.create_async")
        assert create_payment_intent_mock.call_count == 1
        assert create_payment_intent_mock.call_args_list[0].kwargs["customer"] == fetched_account.stripe_customer_id
        assert create_payment_intent_mock.call_args_list[0].kwargs["receipt_email"] == fetched_account.email
        assert create_payment_intent_mock.call_args_list[0].kwargs["capture_method"] == "manual"

        assert (
            create_payment_intent_mock.call_args_list[0].kwargs["amount"]
            == self.get_mock_eventbrite_ticket_class_batch_cost() * outing.headcount
        )

        create_customer_mock = self.get_mock("stripe.Customer.create_async")
        assert create_customer_mock.call_count == 1
        assert create_customer_mock.call_args_list[0].kwargs["metadata"]["vivial_account_id"] == str(account.id)

        create_customer_session_mock = self.get_mock("stripe.CustomerSession.create_async")
        assert create_customer_session_mock.call_count == 1
        assert create_customer_session_mock.call_args_list[0].kwargs["customer"] == fetched_account.stripe_customer_id

        assert self.get_mock("SendGridAPIClient.send").call_count == 0

    async def test_create_payment_intent_with_existing_customer_id_doesnt_create_stripe_customer_account(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            account.stripe_customer_id = self.anystr("stripe_customer_id")

            survey = self.make_survey(session, account)
            # survey.budget = OutingBudget.EXPENSIVE
            outing = self.make_outing(session, account, survey)

        assert self.get_mock("stripe.Customer.create_async").call_count == 0

        self.set_mock_eventbrite_ticket_class_batch(max_cost_cents=survey.budget.upper_limit_cents)

        response = await self.make_graphql_request(
            "initiateBooking",
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

        assert result.data["viewer"]["initiateBooking"]["__typename"] == "InitiateBookingSuccess"
        assert self.get_mock("stripe.Customer.create_async").call_count == 0
        assert self.get_mock("stripe.CustomerSession.create_async").call_count == 1
        assert self.get_mock("SendGridAPIClient.send").call_count == 0

        assert result.data["viewer"]["initiateBooking"]["customerSession"]["clientSecret"] is not None
        async with self.db_session.begin() as session:
            fetched_account = await AccountOrm.get_one(session, account.id)

        assert fetched_account.stripe_customer_id == self.getstr("stripe_customer_id")

    async def test_create_payment_intent_with_missing_client_secret(self) -> None:
        self.mock_stripe_payment_intent.client_secret = None

        async with self.db_session.begin() as session:
            assert await self.count(session, StripePaymentIntentReferenceOrm) == 0
            account = self.make_account(session)
            account.stripe_customer_id = self.anystr("sripe_customer_id")

            survey = self.make_survey(session, account)
            outing = self.make_outing(session, account, survey)

        self.mock_eventbrite_ticket_class_batch = [
            TicketClass(
                id=self.anydigits(),
                cost=CurrencyCost(
                    currency="usd",
                    display=self.anystr(),
                    major_value=self.anystr(),
                    value=self.anyint(max=survey.budget.upper_limit_cents),
                ),
                fee=CurrencyCost(
                    currency="usd",
                    display=self.anystr(),
                    major_value=self.anystr(),
                    value=0,
                ),
                tax=CurrencyCost(
                    currency="usd",
                    display=self.anystr(),
                    major_value=self.anystr(),
                    value=0,
                ),
            )
        ]

        response = await self.make_graphql_request(
            "initiateBooking",
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

        assert result.data["viewer"]["initiateBooking"]["__typename"] == "InitiateBookingFailure"
        assert result.data["viewer"]["initiateBooking"]["failureReason"] == "PAYMENT_INTENT_FAILED"

        async with self.db_session.begin() as session:
            assert await self.count(session, StripePaymentIntentReferenceOrm) == 0

        assert self.get_mock("SendGridAPIClient.send").call_count == 0

    async def test_initiate_booking_auto_confirm_with_paid_outing(self) -> None:
        assert self.get_mock("stripe.PaymentIntent.create_async").call_count == 0
        assert self.get_mock("stripe.Customer.create_async").call_count == 0
        assert self.get_mock("stripe.CustomerSession.create_async").call_count == 0
        assert self.get_mock("SendGridAPIClient.send").call_count == 0

        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 0
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            outing = self.make_outing(session, account, survey)

        self.mock_eventbrite_ticket_class_batch = [
            TicketClass(
                id=self.anydigits(),
                cost=CurrencyCost(
                    currency="usd",
                    display=self.anystr(),
                    major_value=self.anystr(),
                    value=self.anyint(max=survey.budget.upper_limit_cents),
                ),
                fee=CurrencyCost(
                    currency="usd",
                    display=self.anystr(),
                    major_value=self.anystr(),
                    value=0,
                ),
                tax=CurrencyCost(
                    currency="usd",
                    display=self.anystr(),
                    major_value=self.anystr(),
                    value=0,
                ),
            )
        ]

        self.mock_stripe_payment_intent.amount = self.get_mock_eventbrite_ticket_class_batch_cost() * survey.headcount

        response = await self.make_graphql_request(
            "initiateBooking",
            {
                "input": {
                    "outingId": str(outing.id),
                    "autoConfirm": True,
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["initiateBooking"]
        assert data["__typename"] == "InitiateBookingSuccess"

        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 1
            booking = await BookingOrm.get_one(session, UUID(data["booking"]["id"]))

        assert booking.state == BookingState.CONFIRMED

        assert self.get_mock("stripe.PaymentIntent.create_async").call_count == 1
        assert self.get_mock("stripe.PaymentIntent.create_async").call_args_list[0].kwargs["confirm"] is True
        assert (
            self.get_mock("stripe.PaymentIntent.create_async")
            .call_args_list[0]
            .kwargs["automatic_payment_methods"]["enabled"]
            is True
        )

        assert self.get_mock("stripe.Customer.create_async").call_count == 1
        assert self.get_mock("stripe.CustomerSession.create_async").call_count == 1
        assert self.get_mock("SendGridAPIClient.send").call_count == 1

    async def test_initiate_booking_auto_confirm_with_paid_outing_with_payment_method_id_given(self) -> None:
        assert self.get_mock("stripe.PaymentIntent.create_async").call_count == 0
        assert self.get_mock("stripe.Customer.create_async").call_count == 0
        assert self.get_mock("stripe.CustomerSession.create_async").call_count == 0
        assert self.get_mock("SendGridAPIClient.send").call_count == 0

        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 0
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            survey.budget = OutingBudget.EXPENSIVE
            outing = self.make_outing(session, account, survey)

        self.set_mock_eventbrite_ticket_class_batch(max_cost_cents=survey.budget.upper_limit_cents)
        self.mock_stripe_payment_intent.amount = self.get_mock_eventbrite_ticket_class_batch_cost() * survey.headcount

        response = await self.make_graphql_request(
            "initiateBooking",
            {
                "input": {
                    "outingId": str(outing.id),
                    "autoConfirm": True,
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["initiateBooking"]
        assert data["__typename"] == "InitiateBookingSuccess"

        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 1
            booking = await BookingOrm.get_one(session, UUID(data["booking"]["id"]))

        assert booking.state == BookingState.CONFIRMED

        assert self.get_mock("stripe.PaymentIntent.create_async").call_count == 1
        assert self.get_mock("stripe.PaymentIntent.create_async").call_args_list[0].kwargs["confirm"] is True
        assert (
            self.get_mock("stripe.PaymentIntent.create_async")
            .call_args_list[0]
            .kwargs["automatic_payment_methods"]["enabled"]
            is True
        )
        assert self.get_mock("stripe.PaymentIntent.create_async").call_args_list[0].kwargs[
            "payment_method"
        ] == self.getstr("payment method id")

        assert self.get_mock("stripe.Customer.create_async").call_count == 1
        assert self.get_mock("stripe.CustomerSession.create_async").call_count == 1
        assert self.get_mock("SendGridAPIClient.send").call_count == 1

    async def test_initiate_booking_auto_confirm_with_free_outing(self) -> None:
        assert self.get_mock("stripe.PaymentIntent.create_async").call_count == 0
        assert self.get_mock("stripe.Customer.create_async").call_count == 0
        assert self.get_mock("stripe.CustomerSession.create_async").call_count == 0
        assert self.get_mock("SendGridAPIClient.send").call_count == 0

        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 0
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            outing = self.make_outing(session, account, survey)

        self.set_mock_eventbrite_ticket_class_batch(max_cost_cents=0)

        response = await self.make_graphql_request(
            "initiateBooking",
            {
                "input": {
                    "outingId": str(outing.id),
                    "autoConfirm": True,
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["initiateBooking"]
        assert data["__typename"] == "InitiateBookingSuccess"

        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 1
            booking = await BookingOrm.get_one(session, UUID(data["booking"]["id"]))

        assert booking.state == BookingState.CONFIRMED

        assert self.get_mock("stripe.PaymentIntent.create_async").call_count == 0
        assert self.get_mock("stripe.Customer.create_async").call_count == 0
        assert self.get_mock("stripe.CustomerSession.create_async").call_count == 0
        assert self.get_mock("SendGridAPIClient.send").call_count == 1
