from eave.core.lib.address import Address
from eave.core.orm.booking import BookingActivityTemplateOrm, BookingOrm, BookingReservationTemplateOrm
from eave.core.shared.enums import ActivitySource, RestaurantSource
from eave.core.shared.geo import GeoPoint

from ..base import BaseTestCase


class TestBookedOutingsResolver(BaseTestCase):
    async def test_booked_outings_with_activity_and_restaurant(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            reserver_details = self.make_reserver_details(session, account)

            booking = BookingOrm(
                session,
                survey=survey,
                accounts=[account],
                reserver_details=reserver_details,
            )

            booking_activity_template = BookingActivityTemplateOrm(
                session,
                booking=booking,
                name=self.anystr("activity_name"),
                start_time_utc=self.anydatetime("activity_start_time"),
                timezone=self.anytimezone("activity_timezone"),
                photo_uri=self.anyurl("activity_photo_uri"),
                headcount=self.anyint(min=1, max=2),
                coordinates=GeoPoint(
                    lat=self.anylatitude(),
                    lon=self.anylongitude(),
                ),
                external_booking_link=self.anyurl(),
                source=ActivitySource.EVENTBRITE,
                source_id=self.anydigits(),
                address=Address(
                    address1=self.anystr(),
                    address2=self.anystr(),
                    city=self.anystr(),
                    country="US",
                    state=self.anyusstate(),
                    zip_code=self.anydigits(),
                ),
            )
            booking.activities.append(booking_activity_template)

            booking_reservation_template = BookingReservationTemplateOrm(
                session,
                booking=booking,
                name=self.anystr("reservation_name"),
                photo_uri=self.anyurl("reservation_photo_uri"),
                start_time_utc=self.anydatetime("reservation_start_time"),
                timezone=self.anytimezone("reservation_timezone"),
                headcount=self.anyint(min=1, max=2),
                coordinates=GeoPoint(
                    lat=self.anylatitude(),
                    lon=self.anylongitude(),
                ),
                external_booking_link=self.anyurl(),
                source=RestaurantSource.GOOGLE_PLACES,
                source_id=self.anydigits(),
                address=Address(
                    address1=self.anystr(),
                    address2=self.anystr(),
                    city=self.anystr(),
                    country="US",
                    state=self.anyusstate(),
                    zip_code=self.anydigits(),
                ),
            )
            booking.reservations.append(booking_reservation_template)

        response = await self.make_graphql_request(
            "listBookedOutings",
            {},
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["bookedOutings"]
        assert len(data) == 1

        assert data[0]["id"] == str(booking.id)
        assert data[0]["activityName"] == self.getstr("activity_name")
        assert (
            data[0]["activityStartTime"]
            == self.getdatetime("activity_start_time").astimezone(self.gettimezone("activity_timezone")).isoformat()
        )
        assert data[0]["restaurantName"] == self.getstr("reservation_name")
        assert (
            data[0]["restaurantArrivalTime"]
            == self.getdatetime("reservation_start_time")
            .astimezone(self.gettimezone("reservation_timezone"))
            .isoformat()
        )
        assert data[0]["photoUri"] == self.geturl("activity_photo_uri")

    async def test_booked_outings_details(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            survey = self.make_survey(session, account)
            reserver_details = self.make_reserver_details(session, account)
            booking = self.make_booking(session, account, survey, reserver_details)

        response = await self.make_graphql_request(
            "bookingDetails",
            {
                "input": {
                    "bookingId": str(booking.id),
                }
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["bookingDetails"]

        assert data["id"] == str(booking.id)
