from eave.core.orm.booking import BookingActivityTemplateOrm, BookingOrm, BookingReservationTemplateOrm
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.core.shared.address import Address
from eave.core.shared.enums import ActivitySource, RestaurantSource
from eave.core.shared.geo import GeoPoint

from ..base import BaseTestCase


class TestBookedOutingsResolver(BaseTestCase):
    async def test_booked_outings_with_activity_and_restaurant(self) -> None:
        async with self.db_session.begin() as db_session:
            account = self.make_account(db_session)
            reserver_details = ReserverDetailsOrm(
                account=account,
                first_name=self.anyalpha(),
                last_name=self.anyalpha(),
                phone_number=self.anyphonenumber(),
            )
            db_session.add(reserver_details)

            booking = BookingOrm(
                reserver_details=reserver_details,
            )
            db_session.add(booking)

            booking_activity_template = BookingActivityTemplateOrm(
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
                    zip=self.anydigits(),
                ),
            )
            booking.activities.append(booking_activity_template)

            booking_reservation_template = BookingReservationTemplateOrm(
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
                    zip=self.anydigits(),
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
