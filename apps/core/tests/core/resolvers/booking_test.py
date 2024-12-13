from uuid import UUID

import stripe
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

            survey = SurveyOrm(
                account=account,
                visitor_id=self.anyuuid(),
                start_time_utc=self.anydatetime(offset=2 * 60 * 60 * 24),
                timezone=self.anytimezone(),
                search_area_ids=[SearchRegionOrm.all()[0].id],
                budget=OutingBudget.INEXPENSIVE,
                headcount=self.anyint(min=1, max=2),
            )
            session.add(survey)

            outing = OutingOrm(
                visitor_id=self.anyuuid(),
                account=account,
                survey=survey,
            )
            session.add(outing)

            outing.activities.append(
                OutingActivityOrm(
                    outing=outing,
                    headcount=survey.headcount,
                    source=ActivitySource.EVENTBRITE,
                    source_id=self.anystr("activity.source_id"),
                    start_time_utc=survey.start_time_utc,
                    timezone=survey.timezone,
                )
            )

            outing.reservations.append(
                OutingReservationOrm(
                    outing=outing,
                    headcount=survey.headcount,
                    source=RestaurantSource.GOOGLE_PLACES,
                    source_id=self.anystr("reservation.source_id"),
                    start_time_utc=survey.start_time_utc,
                    timezone=survey.timezone,
                )
            )

            reserver_details = ReserverDetailsOrm(
                account=account,
                first_name=self.anystr(),
                last_name=self.anystr(),
                phone_number=self.anyphonenumber(),
            )
            session.add(reserver_details)

            stripe_payment_intent_reference = StripePaymentIntentReferenceOrm(
                account=account,
                outing=outing,
                stripe_payment_intent_id=self.getstr("stripe.PaymentIntent.id"),
            )
            session.add(stripe_payment_intent_reference)

        self.mock_stripe_payment_intent.amount = self.getint("eventbrite.TicketClass.0.cost.value") + self.getint("eventbrite.TicketClass.0.fee.value") + self.getint("eventbrite.TicketClass.0.tax.value")

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
        assert self.get_mock("slack client").call_count == 1

    async def test_create_booking_from_expired_outing_fails(self) -> None:
        async with self.db_session.begin() as session:
            account = AccountOrm(email=self.anyemail(), plaintext_password=self.anystr())
            session.add(account)

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

            outing = OutingOrm(
                visitor_id=self.anyuuid(),
                account=account,
                survey=survey,
            )
            session.add(outing)

            reserver_details = ReserverDetailsOrm(
                account=account,
                first_name=self.anystr(),
                last_name=self.anystr(),
                phone_number=self.anyphonenumber(),
            )
            session.add(reserver_details)

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
