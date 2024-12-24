from eave.core.orm.booking import BookingOrm
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.shared.enums import BookingState, OutingBudget
from eave.stdlib.time import ONE_YEAR_IN_SECONDS

from ..base import BaseTestCase


class TestConfirmBookingResolver(BaseTestCase):
    async def test_confirm_booking_with_no_reserver_details_set(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            outing = self.make_outing(session, account, survey)
            reserver_details = self.make_reserver_details(session, account)
            _reserver_details_alt = self.make_reserver_details(session, account)
            stripe_payment_intent_reference = self.make_stripe_payment_intent_reference(session, account)
            booking = self.make_booking(
                session,
                account,
                outing,
                stripe_payment_intent_reference=stripe_payment_intent_reference,
                reserver_details=None,
            )

        assert booking.state == BookingState.INITIATED

        self.mock_stripe_payment_intent.amount = self.get_mock_eventbrite_ticket_class_batch_cost() * booking.headcount
        assert self.get_mock("stripe.PaymentIntent.retrieve_async").call_count == 0
        assert self.get_mock("slack client").call_count == 0
        assert self.get_mock("SendGridAPIClient.send").call_count == 0

        response = await self.make_graphql_request(
            "confirmBooking",
            {
                "input": {
                    "bookingId": str(booking.id),
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["confirmBooking"]
        assert data["__typename"] == "ConfirmBookingSuccess"
        assert data["booking"]["reserverDetails"]["id"] == str(reserver_details.id)

        async with self.db_session.begin() as session:
            booking_fetched = await BookingOrm.get_one(session, booking.id)
            assert booking_fetched.state == BookingState.CONFIRMED
            assert booking_fetched.reserver_details is not None
            assert booking_fetched.reserver_details.id == reserver_details.id

        assert self.get_mock("stripe.PaymentIntent.retrieve_async").call_count == 1
        assert self.get_mock("slack client").call_count == 2  # One for parent, one for thread
        assert self.get_mock("SendGridAPIClient.send").call_count == 1

    async def test_confirm_booking_valid(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            outing = self.make_outing(session, account, survey)
            reserver_details = self.make_reserver_details(session, account)
            stripe_payment_intent_reference = self.make_stripe_payment_intent_reference(session, account)
            booking = self.make_booking(
                session,
                account,
                outing,
                stripe_payment_intent_reference=stripe_payment_intent_reference,
                reserver_details=reserver_details,
            )

        assert booking.state == BookingState.INITIATED

        self.mock_stripe_payment_intent.amount = self.get_mock_eventbrite_ticket_class_batch_cost() * booking.headcount
        assert self.get_mock("stripe.PaymentIntent.retrieve_async").call_count == 0
        assert self.get_mock("slack client").call_count == 0
        assert self.get_mock("SendGridAPIClient.send").call_count == 0

        response = await self.make_graphql_request(
            "confirmBooking",
            {
                "input": {
                    "bookingId": str(booking.id),
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["confirmBooking"]
        assert data["__typename"] == "ConfirmBookingSuccess"
        assert data["booking"]["id"] == str(booking.id)
        assert data["booking"]["reserverDetails"]["id"] == str(reserver_details.id)

        async with self.db_session.begin() as session:
            booking_fetched = await BookingOrm.get_one(session, booking.id)
            assert booking_fetched.state == BookingState.CONFIRMED

        assert self.get_mock("stripe.PaymentIntent.retrieve_async").call_count == 1
        assert self.get_mock("slack client").call_count == 2  # One for parent, one for thread
        assert self.get_mock("SendGridAPIClient.send").call_count == 1

    async def test_confirm_booking_with_unauthorized_account_for_booking(self) -> None:
        async with self.db_session.begin() as session:
            account1 = self.make_account(session)
            account2 = self.make_account(session)
            survey = self.make_survey(session, account1)
            outing = self.make_outing(session, account1, survey)
            booking = self.make_booking(session, account1, outing)

        response = await self.make_graphql_request(
            "confirmBooking",
            {
                "input": {
                    "bookingId": str(booking.id),
                },
            },
            account_id=account2.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["confirmBooking"]
        assert "booking" not in data
        assert data["__typename"] == "ConfirmBookingFailure"
        assert data["failureReason"] == "BOOKING_NOT_FOUND"

        async with self.db_session.begin() as session:
            booking_fetched = await BookingOrm.get_one(session, booking.id)
            assert booking_fetched.state == BookingState.INITIATED

        assert self.get_mock("SendGridAPIClient.send").call_count == 0

    async def test_confirm_booking_with_incorrect_payment_intent_status(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            outing = self.make_outing(session, account, survey)
            stripe_payment_intent_reference = self.make_stripe_payment_intent_reference(session, account)
            booking = self.make_booking(
                session, account, outing, stripe_payment_intent_reference=stripe_payment_intent_reference
            )

        self.mock_stripe_payment_intent.status = "requires_action"

        response = await self.make_graphql_request(
            "confirmBooking",
            {
                "input": {
                    "bookingId": str(booking.id),
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["confirmBooking"]
        assert "booking" not in data
        assert data["__typename"] == "ConfirmBookingFailure"
        assert data["failureReason"] == "PAYMENT_REQUIRED"

        assert self.get_mock("SendGridAPIClient.send").call_count == 0

    async def test_confirm_booking_free(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            outing = self.make_outing(session, account, survey)
            reserver_details = self.make_reserver_details(session, account)
            booking = self.make_booking(session, account, outing, reserver_details=reserver_details)

        assert booking.state == BookingState.INITIATED

        self.mock_eventbrite_ticket_class_batch = []
        assert self.get_mock("stripe.PaymentIntent.retrieve_async").call_count == 0
        assert self.get_mock("slack client").call_count == 0
        assert self.get_mock("SendGridAPIClient.send").call_count == 0

        response = await self.make_graphql_request(
            "confirmBooking",
            {
                "input": {
                    "bookingId": str(booking.id),
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["confirmBooking"]
        assert data["__typename"] == "ConfirmBookingSuccess"
        assert data["booking"]["id"] == str(booking.id)
        assert data["booking"]["reserverDetails"]["id"] == str(reserver_details.id)

        async with self.db_session.begin() as session:
            booking_fetched = await BookingOrm.get_one(session, booking.id)
            assert booking_fetched.state == BookingState.CONFIRMED

        assert self.get_mock("stripe.PaymentIntent.retrieve_async").call_count == 0
        assert self.get_mock("slack client").call_count == 2  # One for parent, one for thread
        assert self.get_mock("SendGridAPIClient.send").call_count == 1

    async def test_confirm_booking_with_outing_amount_more_than_intent_amount(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            outing = self.make_outing(session, account, survey)
            stripe_payment_intent_reference = self.make_stripe_payment_intent_reference(session, account)
            booking = self.make_booking(
                session, account, outing, stripe_payment_intent_reference=stripe_payment_intent_reference
            )

        assert self.get_mock("stripe.PaymentIntent.retrieve_async").call_count == 0
        assert self.get_mock("slack client").call_count == 0

        self.mock_stripe_payment_intent.amount = (
            self.get_mock_eventbrite_ticket_class_batch_cost() * booking.headcount
        ) - 1000

        response = await self.make_graphql_request(
            "confirmBooking",
            {
                "input": {
                    "bookingId": str(booking.id),
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["confirmBooking"]
        assert data["__typename"] == "ConfirmBookingFailure"
        assert data["failureReason"] == "PAYMENT_REQUIRED"

        async with self.db_session.begin() as session:
            booking_fetched = await BookingOrm.get_one(session, booking.id)
            assert booking_fetched.state == BookingState.INITIATED

        assert self.get_mock("stripe.PaymentIntent.retrieve_async").call_count == 1
        assert self.get_mock("slack client").call_count == 0
        assert self.get_mock("SendGridAPIClient.send").call_count == 0

    async def test_confirm_booking_with_outing_amount_less_than_intent_amount(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            outing = self.make_outing(session, account, survey)
            reserver_details = self.make_reserver_details(session, account)
            stripe_payment_intent_reference = self.make_stripe_payment_intent_reference(session, account)
            booking = self.make_booking(
                session,
                account,
                outing,
                reserver_details=reserver_details,
                stripe_payment_intent_reference=stripe_payment_intent_reference,
            )

        assert self.get_mock("stripe.PaymentIntent.retrieve_async").call_count == 0
        assert self.get_mock("slack client").call_count == 0
        assert self.get_mock("SendGridAPIClient.send").call_count == 0

        self.mock_stripe_payment_intent.amount = (
            self.get_mock_eventbrite_ticket_class_batch_cost() * booking.headcount
        ) + 1000

        response = await self.make_graphql_request(
            "confirmBooking",
            {
                "input": {
                    "bookingId": str(booking.id),
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["confirmBooking"]
        assert data["__typename"] == "ConfirmBookingSuccess"

        async with self.db_session.begin() as session:
            booking_fetched = await BookingOrm.get_one(session, booking.id)
            assert booking_fetched.state == BookingState.CONFIRMED

        assert self.get_mock("stripe.PaymentIntent.retrieve_async").call_count == 1
        assert self.get_mock("slack client").call_count == 2
        assert self.get_mock("SendGridAPIClient.send").call_count == 1

    async def test_confirm_booking_with_already_confirmed_booking(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            outing = self.make_outing(session, account, survey)
            reserver_details = self.make_reserver_details(session, account)
            stripe_payment_intent_reference = self.make_stripe_payment_intent_reference(session, account)
            booking = self.make_booking(
                session,
                account,
                outing,
                reserver_details=reserver_details,
                stripe_payment_intent_reference=stripe_payment_intent_reference,
            )
            booking.state = BookingState.CONFIRMED

        assert self.get_mock("stripe.PaymentIntent.retrieve_async").call_count == 0
        assert self.get_mock("slack client").call_count == 0
        assert self.get_mock("SendGridAPIClient.send").call_count == 0

        response = await self.make_graphql_request(
            "confirmBooking",
            {
                "input": {
                    "bookingId": str(booking.id),
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["confirmBooking"]
        assert data["__typename"] == "ConfirmBookingSuccess"

        async with self.db_session.begin() as session:
            booking_fetched = await BookingOrm.get_one(session, booking.id)
            assert booking_fetched.state == BookingState.CONFIRMED

        assert self.get_mock("stripe.PaymentIntent.retrieve_async").call_count == 0
        assert self.get_mock("slack client").call_count == 0
        assert self.get_mock("SendGridAPIClient.send").call_count == 0

    async def test_confirm_booking_without_payment_intent_when_payment_required(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            survey.budget = OutingBudget.EXPENSIVE
            outing = self.make_outing(session, account, survey)
            reserver_details = self.make_reserver_details(session, account)
            booking = self.make_booking(
                session,
                account,
                outing,
                reserver_details=reserver_details,
                stripe_payment_intent_reference=None,
            )

        assert self.get_mock("stripe.PaymentIntent.retrieve_async").call_count == 0
        assert self.get_mock("slack client").call_count == 0

        self.set_mock_eventbrite_ticket_class_batch(max_cost_cents=survey.budget.upper_limit_cents)

        response = await self.make_graphql_request(
            "confirmBooking",
            {
                "input": {
                    "bookingId": str(booking.id),
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["confirmBooking"]
        assert data["__typename"] == "ConfirmBookingFailure"
        assert data["failureReason"] == "PAYMENT_REQUIRED"

        async with self.db_session.begin() as session:
            booking_fetched = await BookingOrm.get_one(session, booking.id)
            assert booking_fetched.state == BookingState.INITIATED

        assert self.get_mock("stripe.PaymentIntent.retrieve_async").call_count == 0
        assert self.get_mock("slack client").call_count == 0
        assert self.get_mock("SendGridAPIClient.send").call_count == 0

    async def test_confirm_booking_from_expired_outing_fails(self) -> None:
        async with self.db_session.begin() as session:
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
            booking = self.make_booking(session, account, outing)

        response = await self.make_graphql_request(
            "confirmBooking",
            {
                "input": {
                    "bookingId": str(booking.id),
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["confirmBooking"]
        assert "booking" not in data
        assert data["failureReason"] == "START_TIME_TOO_SOON"

        assert self.get_mock("SendGridAPIClient.send").call_count == 0

    async def test_confirm_booking_from_too_far_future_outing_fails(self) -> None:
        async with self.db_session.begin() as session:
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
            booking = self.make_booking(session, account, outing)

        response = await self.make_graphql_request(
            "confirmBooking",
            {
                "input": {
                    "bookingId": str(booking.id),
                },
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["confirmBooking"]
        assert "booking" not in data
        assert data["failureReason"] == "START_TIME_TOO_LATE"

        assert self.get_mock("SendGridAPIClient.send").call_count == 0
