from eave.core.orm.booking import BookingOrm
from eave.core.orm.booking_activities_template import BookingActivityTemplateOrm
from eave.core.orm.booking_reservations_template import BookingReservationTemplateOrm
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.core.shared.address import Address
from eave.core.shared.enums import ActivitySource, RestaurantSource

from ..base import BaseTestCase


class TestBookedOutingsResolver(BaseTestCase):
    async def test_booked_outings_with_activity_and_restaurant(self) -> None:
        async with self.db_session.begin() as db_session:
            account = await self.make_account(db_session)
            reserver_details = await ReserverDetailsOrm.build(
                account_id=account.id,
                first_name=self.anyalpha(),
                last_name=self.anyalpha(),
                phone_number=self.anyphonenumber(),
            ).save(db_session)

            booking = await BookingOrm.build(
                account_id=account.id,
                reserver_details_id=reserver_details.id,
            ).save(db_session)

            await BookingActivityTemplateOrm.build(
                booking_id=booking.id,
                name=self.anystr("activity_name"),
                start_time_utc=self.anydatetime("activity_start_time"),
                timezone=self.anytimezone("activity_timezone"),
                photo_uri=self.anyurl("activity_photo_uri"),
                headcount=self.anyint(min=1, max=2),
                lat=self.anylatitude(),
                lon=self.anylongitude(),
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
            ).save(db_session)

            await BookingReservationTemplateOrm.build(
                booking_id=booking.id,
                name=self.anystr("reservation_name"),
                photo_uri=self.anyurl("reservation_photo_uri"),
                start_time_utc=self.anydatetime("reservation_start_time"),
                timezone=self.anytimezone("reservation_timezone"),
                headcount=self.anyint(min=1, max=2),
                lat=self.anylatitude(),
                lon=self.anylongitude(),
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
            ).save(db_session)

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
        assert data[0]["activityStartTime"] == self.getdatetime("activity_start_time").astimezone(
            self.gettimezone("activity_timezone")
        )
        assert data[0]["restaurantName"] == self.getstr("reservation_name")
        assert data[0]["restaurantArrivalTime"] == self.getdatetime("reservation_start_time").astimezone(
            self.gettimezone("reservation_timezone")
        )
        assert data[0]["photoUri"] == self.geturl("activity_photo_uri")
