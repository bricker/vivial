from datetime import UTC

from eave.core.lib.address import Address
from eave.core.orm.booking import BookingActivityTemplateOrm, BookingOrm, BookingReservationTemplateOrm
from eave.core.orm.stripe_payment_intent_reference import StripePaymentIntentReferenceOrm
from eave.core.shared.enums import ActivitySource, RestaurantSource
from eave.core.shared.geo import GeoPoint

from ..base import BaseTestCase


class TestBookingOrms(BaseTestCase):
    async def test_booking_associations(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            reserver_details = self.make_reserver_details(session, account)
            survey = self.make_survey(session, account)
            outing = self.make_outing(session, account, survey)

            stripe_payment_intent_reference = StripePaymentIntentReferenceOrm(
                session,
                account=account,
                stripe_payment_intent_id=self.anystr(),
                outing=outing,
            )

            booking_new = BookingOrm(
                session,
                accounts=[account],
                survey=survey,
                reserver_details=reserver_details,
                stripe_payment_intent_reference=stripe_payment_intent_reference,
            )

            booking_activity = BookingActivityTemplateOrm(
                session,
                booking=booking_new,
                name=self.anystr("activity.name"),
                start_time_utc=self.anydatetime("activity.start_time_utc"),
                timezone=self.anytimezone("activity.timezone"),
                photo_uri=self.anyurl("activity.photo_uri"),
                headcount=self.anyint("activity.headcount", min=1, max=2),
                coordinates=GeoPoint(
                    lat=self.anylatitude("activity.lat"),
                    lon=self.anylongitude("activity.lon"),
                ),
                external_booking_link=self.anyurl("activity.external_booking_link"),
                source=ActivitySource.EVENTBRITE,
                source_id=self.anydigits("activity.source_id"),
                address=Address(
                    address1=self.anystr("activity.address.address1"),
                    address2=self.anystr("activity.address.address2"),
                    city=self.anystr("activity.address.city"),
                    state=self.anyusstate("activity.address.state"),
                    zip_code=self.anydigits("activity.address.zip"),
                    country="US",
                ),
            )

            booking_new.activities.append(booking_activity)

            booking_reservation = BookingReservationTemplateOrm(
                session,
                booking=booking_new,
                name=self.anystr("reservation.name"),
                start_time_utc=self.anydatetime("reservation.start_time_utc"),
                timezone=self.anytimezone("reservation.timezone"),
                photo_uri=self.anyurl("reservation.photo_uri"),
                headcount=self.anyint("reservation.headcount", min=1, max=2),
                coordinates=GeoPoint(
                    lat=self.anylatitude("reservation.lat"),
                    lon=self.anylongitude("reservation.lon"),
                ),
                external_booking_link=self.anyurl("reservation.external_booking_link"),
                source=RestaurantSource.GOOGLE_PLACES,
                source_id=self.anydigits("reservation.source_id"),
                address=Address(
                    address1=self.anystr("reservation.address.address1"),
                    address2=self.anystr("reservation.address.address2"),
                    city=self.anystr("reservation.address.city"),
                    state=self.anyusstate("reservation.address.state"),
                    zip_code=self.anydigits("reservation.address.zip"),
                    country="US",
                ),
            )
            booking_new.reservations.append(booking_reservation)

        async with self.db_session.begin() as session:
            booking_fetched = await BookingOrm.get_one(session, booking_new.id)

            assert len(booking_fetched.accounts) == 1
            assert booking_fetched.accounts[0].id == account.id

            assert booking_fetched.reserver_details.id == reserver_details.id
            assert booking_fetched.reserver_details_id == reserver_details.id

            assert booking_fetched.stripe_payment_intent_reference is not None
            assert booking_fetched.stripe_payment_intent_reference_id is not None
            assert booking_fetched.stripe_payment_intent_reference.id == stripe_payment_intent_reference.id
            assert booking_fetched.stripe_payment_intent_reference_id == stripe_payment_intent_reference.id

            # Taking this opportunity to test the initializers too, since we already setup all the prerequisite records.

            assert len(booking_fetched.activities) == 1
            first_activity = booking_fetched.activities[0]
            assert first_activity.id == booking_activity.id
            assert first_activity.booking.id == booking_new.id

            assert len(booking_fetched.reservations) == 1
            first_reservation = booking_fetched.reservations[0]
            assert first_reservation.id == booking_reservation.id
            assert first_reservation.booking.id == booking_new.id

    async def test_booking_activity_template_orm_initialization(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            reserver_details = self.make_reserver_details(session, account)

            booking = BookingOrm(
                session,
                accounts=[account],
                survey=survey,
                reserver_details=reserver_details,
            )

            booking_activity_template_new = BookingActivityTemplateOrm(
                session,
                booking=booking,
                name=self.anystr("activity.name"),
                start_time_utc=self.anydatetime("activity.start_time_utc"),
                timezone=self.anytimezone("activity.timezone"),
                photo_uri=self.anyurl("activity.photo_uri"),
                headcount=self.anyint("activity.headcount", min=1, max=2),
                coordinates=GeoPoint(
                    lat=self.anylatitude("activity.lat"),
                    lon=self.anylongitude("activity.lon"),
                ),
                external_booking_link=self.anyurl("activity.external_booking_link"),
                source=ActivitySource.EVENTBRITE,
                source_id=self.anydigits("activity.source_id"),
                address=Address(
                    address1=self.anystr("activity.address.address1"),
                    address2=self.anystr("activity.address.address2"),
                    city=self.anystr("activity.address.city"),
                    state=self.anyusstate("activity.address.state"),
                    zip_code=self.anydigits("activity.address.zip"),
                    country="US",
                ),
            )

        async with self.db_session.begin() as session:
            booking_activity_template_fetched = await session.get_one(
                BookingActivityTemplateOrm, booking_activity_template_new.id
            )

            assert booking_activity_template_fetched.id == booking_activity_template_new.id
            assert booking_activity_template_fetched.booking.id == booking.id
            assert booking_activity_template_fetched.name == self.getstr("activity.name")
            assert booking_activity_template_fetched.start_time_utc == self.getdatetime("activity.start_time_utc")
            assert booking_activity_template_fetched.start_time_utc.tzinfo == UTC
            assert booking_activity_template_fetched.timezone == self.gettimezone("activity.timezone")
            assert booking_activity_template_fetched.start_time_local == self.getdatetime(
                "activity.start_time_utc"
            ).astimezone(self.gettimezone("activity.timezone"))

            assert booking_activity_template_fetched.photo_uri == self.geturl("activity.photo_uri")
            assert booking_activity_template_fetched.headcount == self.getint("activity.headcount")
            assert (
                booking_activity_template_fetched.coordinates
                == GeoPoint(
                    lat=self.getlatitude("activity.lat"), lon=self.getlongitude("activity.lon")
                ).geoalchemy_shape()
            )
            assert booking_activity_template_fetched.external_booking_link == self.geturl(
                "activity.external_booking_link"
            )
            assert booking_activity_template_fetched.source == ActivitySource.EVENTBRITE
            assert booking_activity_template_fetched.source_id == self.getdigits("activity.source_id")
            assert booking_activity_template_fetched.address == Address(
                address1=self.getstr("activity.address.address1"),
                address2=self.getstr("activity.address.address2"),
                city=self.getstr("activity.address.city"),
                state=self.getusstate("activity.address.state"),
                zip_code=self.getdigits("activity.address.zip"),
                country="US",
            )

    async def test_booking_reservation_template_orm_initialization(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            reserver_details = self.make_reserver_details(session, account)

            booking = BookingOrm(
                session,
                accounts=[account],
                survey=survey,
                reserver_details=reserver_details,
            )

            booking_reservation_template_new = BookingReservationTemplateOrm(
                session,
                booking=booking,
                name=self.anystr("reservation.name"),
                start_time_utc=self.anydatetime("reservation.start_time_utc"),
                timezone=self.anytimezone("reservation.timezone"),
                photo_uri=self.anyurl("reservation.photo_uri"),
                headcount=self.anyint("reservation.headcount", min=1, max=2),
                coordinates=GeoPoint(
                    lat=self.anylatitude("reservation.lat"),
                    lon=self.anylongitude("reservation.lon"),
                ),
                external_booking_link=self.anyurl("reservation.external_booking_link"),
                source=RestaurantSource.GOOGLE_PLACES,
                source_id=self.anydigits("reservation.source_id"),
                address=Address(
                    address1=self.anystr("reservation.address.address1"),
                    address2=self.anystr("reservation.address.address2"),
                    city=self.anystr("reservation.address.city"),
                    state=self.anyusstate("reservation.address.state"),
                    zip_code=self.anydigits("reservation.address.zip"),
                    country="US",
                ),
            )

        async with self.db_session.begin() as session:
            booking_reservation_template_fetched = await session.get_one(
                BookingReservationTemplateOrm, booking_reservation_template_new.id
            )

            assert booking_reservation_template_fetched.id == booking_reservation_template_new.id
            assert booking_reservation_template_fetched.booking.id == booking.id
            assert booking_reservation_template_fetched.name == self.getstr("reservation.name")
            assert booking_reservation_template_fetched.start_time_utc == self.getdatetime("reservation.start_time_utc")
            assert booking_reservation_template_fetched.start_time_utc.tzinfo == UTC
            assert booking_reservation_template_fetched.timezone == self.gettimezone("reservation.timezone")
            assert booking_reservation_template_fetched.start_time_local == self.getdatetime(
                "reservation.start_time_utc"
            ).astimezone(self.gettimezone("reservation.timezone"))

            assert booking_reservation_template_fetched.photo_uri == self.geturl("reservation.photo_uri")
            assert booking_reservation_template_fetched.headcount == self.getint("reservation.headcount")
            assert (
                booking_reservation_template_fetched.coordinates
                == GeoPoint(
                    lat=self.getlatitude("reservation.lat"), lon=self.getlongitude("reservation.lon")
                ).geoalchemy_shape()
            )
            assert booking_reservation_template_fetched.external_booking_link == self.geturl(
                "reservation.external_booking_link"
            )
            assert booking_reservation_template_fetched.source == RestaurantSource.GOOGLE_PLACES
            assert booking_reservation_template_fetched.source_id == self.getdigits("reservation.source_id")
            assert booking_reservation_template_fetched.address == Address(
                address1=self.getstr("reservation.address.address1"),
                address2=self.getstr("reservation.address.address2"),
                city=self.getstr("reservation.address.city"),
                state=self.getusstate("reservation.address.state"),
                zip_code=self.getdigits("reservation.address.zip"),
                country="US",
            )
