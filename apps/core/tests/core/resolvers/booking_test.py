from uuid import UUID

from eave.core.orm.account import AccountOrm
from eave.core.orm.booking import BookingOrm
from eave.core.orm.outing import OutingActivityOrm, OutingOrm, OutingReservationOrm
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.orm.stripe_payment_intent_reference import StripePaymentIntentReferenceOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.shared.enums import ActivitySource, OutingBudget, RestaurantSource

from ..base import BaseTestCase


class TestBookingEndpoints(BaseTestCase):
    async def test_valid_create_booking(self) -> None:
        assert self.get_mock("stripe.PaymentIntent.retrieve_async").call_count == 0
        assert self.get_mock("slack client").call_count == 0

        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 0
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            outing = self.make_outing(session, account, survey)
            reserver_details = self.make_reserver_details(session, account)

            stripe_payment_intent_reference = StripePaymentIntentReferenceOrm(
                account=account,
                outing=outing,
                stripe_payment_intent_id=self.getstr("stripe.PaymentIntent.id"),
            )
            session.add(stripe_payment_intent_reference)

        self.mock_stripe_payment_intent.amount = (
            self.getint("eventbrite.TicketClass.0.cost.value")
            + self.getint("eventbrite.TicketClass.0.fee.value")
            + self.getint("eventbrite.TicketClass.0.tax.value")
        )

        response = await self.make_graphql_request(
            "createBooking",
            {
                "input": {
                    "outingId": str(outing.id),
                    "reserverDetailsId": str(reserver_details.id),
                    "paymentIntent": {
                        "id": self.getstr("stripe.PaymentIntent.id"),
                        "clientSecret": self.getstr("stripe.PaymentIntent.client_secret"),
                    },
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["createBooking"]
        assert data["__typename"] == "CreateBookingSuccess"

        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 1
            booking = await BookingOrm.get_one(session, UUID(data["booking"]["id"]))

        assert len(booking.reservations) == 1
        assert booking.reservations[0].source_id == self.getstr("reservation.source_id")

        assert len(booking.activities) == 1
        assert booking.activities[0].source_id == self.getstr("activity.source_id")

        assert self.get_mock("stripe.PaymentIntent.retrieve_async").call_count == 1
        assert self.get_mock("slack client").call_count == 2 # One for parent, one for thread

    async def test_create_booking_with_invalid_payment_intent_fields(self) -> None:
        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 0
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            outing = self.make_outing(session, account, survey)
            reserver_details = self.make_reserver_details(session, account)

        response = await self.make_graphql_request(
            "createBooking",
            {
                "input": {
                    "outingId": str(outing.id),
                    "reserverDetailsId": str(reserver_details.id),
                    "paymentIntent": {
                        "id": "",
                        "clientSecret": "",
                    },
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["createBooking"]
        assert data["__typename"] == "CreateBookingFailure"
        assert data["failureReason"] == "INVALID_PAYMENT_INTENT"

        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 0

    async def test_create_booking_with_mismatched_outings(self) -> None:
        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 0
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            outing = self.make_outing(session, account, survey)
            outing2 = self.make_outing(session, account, survey)
            reserver_details = self.make_reserver_details(session, account)

            stripe_payment_intent_reference = StripePaymentIntentReferenceOrm(
                outing=outing,
                account=account,
                stripe_payment_intent_id=self.getstr("stripe.PaymentIntent.id"),
            )
            session.add(stripe_payment_intent_reference)

        response = await self.make_graphql_request(
            "createBooking",
            {
                "input": {
                    "outingId": str(outing2.id),
                    "reserverDetailsId": str(reserver_details.id),
                    "paymentIntent": {
                        "id": self.getstr("stripe.PaymentIntent.id"),
                        "clientSecret": self.getstr("stripe.PaymentIntent.client_secret"),
                    },
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["createBooking"]
        assert data["__typename"] == "CreateBookingFailure"
        assert data["failureReason"] == "INVALID_PAYMENT_INTENT"

        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 0

    async def test_create_booking_with_incorrect_payment_intent_status(self) -> None:
        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 0
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            outing = self.make_outing(session, account, survey)
            reserver_details = self.make_reserver_details(session, account)

            stripe_payment_intent_reference = StripePaymentIntentReferenceOrm(
                outing=outing,
                account=account,
                stripe_payment_intent_id=self.getstr("stripe.PaymentIntent.id"),
            )
            session.add(stripe_payment_intent_reference)

        self.mock_stripe_payment_intent.status = "requires_action"

        response = await self.make_graphql_request(
            "createBooking",
            {
                "input": {
                    "outingId": str(outing.id),
                    "reserverDetailsId": str(reserver_details.id),
                    "paymentIntent": {
                        "id": self.getstr("stripe.PaymentIntent.id"),
                        "clientSecret": self.getstr("stripe.PaymentIntent.client_secret"),
                    },
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["createBooking"]
        assert data["__typename"] == "CreateBookingFailure"
        assert data["failureReason"] == "PAYMENT_REQUIRED"

        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 0

    async def test_create_booking_free(self) -> None:
        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 0
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            outing = self.make_outing(session, account, survey)
            reserver_details = self.make_reserver_details(session, account)

        self.mock_eventbrite_ticket_class_batch = []

        response = await self.make_graphql_request(
            "createBooking",
            {
                "input": {
                    "outingId": str(outing.id),
                    "reserverDetailsId": str(reserver_details.id),
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["createBooking"]
        assert data["__typename"] == "CreateBookingSuccess"

        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 1

        assert self.get_mock("slack client").call_count == 2 # One for parent, one for thread

    async def test_create_booking_without_payment_intent_payment_required(self) -> None:
        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 0
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            outing = self.make_outing(session, account, survey)
            reserver_details = self.make_reserver_details(session, account)

            stripe_payment_intent_reference = StripePaymentIntentReferenceOrm(
                outing=outing,
                account=account,
                stripe_payment_intent_id=self.getstr("stripe.PaymentIntent.id"),
            )
            session.add(stripe_payment_intent_reference)

        response = await self.make_graphql_request(
            "createBooking",
            {
                "input": {
                    "outingId": str(outing.id),
                    "reserverDetailsId": str(reserver_details.id),
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["createBooking"]
        assert data["__typename"] == "CreateBookingFailure"
        assert data["failureReason"] == "PAYMENT_REQUIRED"

        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 0

    async def test_create_booking_with_mistmatched_amounts(self) -> None:
        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 0
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            outing = self.make_outing(session, account, survey)
            reserver_details = self.make_reserver_details(session, account)

            stripe_payment_intent_reference = StripePaymentIntentReferenceOrm(
                outing=outing,
                account=account,
                stripe_payment_intent_id=self.getstr("stripe.PaymentIntent.id"),
            )
            session.add(stripe_payment_intent_reference)

        self.mock_stripe_payment_intent.amount = self.anyint("payment intent amount") # There is a very small chance this could be the same number as the random prices for the ticket classes.

        response = await self.make_graphql_request(
            "createBooking",
            {
                "input": {
                    "outingId": str(outing.id),
                    "reserverDetailsId": str(reserver_details.id),
                    "paymentIntent": {
                        "id": self.getstr("stripe.PaymentIntent.id"),
                        "clientSecret": self.getstr("stripe.PaymentIntent.client_secret"),
                    },
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["createBooking"]
        assert data["__typename"] == "CreateBookingFailure"
        assert data["failureReason"] == "PAYMENT_REQUIRED"

        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 0

    async def test_create_booking_with_outing_amount_less_than_intent_amount(self) -> None:
        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 0
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            outing = self.make_outing(session, account, survey)
            reserver_details = self.make_reserver_details(session, account)

            stripe_payment_intent_reference = StripePaymentIntentReferenceOrm(
                outing=outing,
                account=account,
                stripe_payment_intent_id=self.getstr("stripe.PaymentIntent.id"),
            )
            session.add(stripe_payment_intent_reference)

        self.mock_stripe_payment_intent.amount += 1000

        response = await self.make_graphql_request(
            "createBooking",
            {
                "input": {
                    "outingId": str(outing.id),
                    "reserverDetailsId": str(reserver_details.id),
                    "paymentIntent": {
                        "id": self.getstr("stripe.PaymentIntent.id"),
                        "clientSecret": self.getstr("stripe.PaymentIntent.client_secret"),
                    },
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["createBooking"]
        assert data["__typename"] == "CreateBookingSuccess"

        async with self.db_session.begin() as session:
            assert await self.count(session, BookingOrm) == 1

    async def test_create_booking_from_expired_outing_fails(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            survey = SurveyOrm(
                account=account,
                visitor_id=self.anyuuid(),
                start_time_utc=self.anydatetime(past=True),
                timezone=self.anytimezone(),
                search_area_ids=[SearchRegionOrm.all()[0].id],
                budget=OutingBudget.INEXPENSIVE,
                headcount=self.anyint(min=1, max=2),
            )
            session.add(survey)

            outing = self.make_outing(session, account, survey)
            reserver_details = self.make_reserver_details(session, account)

        response = await self.make_graphql_request(
            "createBooking",
            {
                "input": {
                    "outingId": str(outing.id),
                    "reserverDetailsId": str(reserver_details.id),
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["createBooking"]
        assert "booking" not in data
        assert data["failureReason"] == "START_TIME_TOO_SOON"
