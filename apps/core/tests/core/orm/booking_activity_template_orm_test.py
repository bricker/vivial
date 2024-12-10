from datetime import UTC

from eave.core.orm.booking import BookingOrm
from eave.core.orm.booking import BookingActivityTemplateOrm
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.core.shared.address import Address
from eave.core.shared.enums import ActivitySource

from ..base import BaseTestCase


class TestBookingActivityTemplateOrm(BaseTestCase):
    async def test_create_booking_activity_template_orm(self) -> None:
        async with self.db_session.begin() as session:
            account = await self.make_account(session)

            reserver_details = await ReserverDetailsOrm.build(
                account_id=account.id,
                first_name=self.anyalpha(),
                last_name=self.anyalpha(),
                phone_number=self.anyphonenumber(),
            ).save(session)

            booking = await BookingOrm.build(
                account_id=account.id,
                reserver_details_id=reserver_details.id,
            ).save(session)

            await BookingActivityTemplateOrm.build(
                booking_id=booking.id,
                name=self.anystr("activity_name"),
                start_time_utc=self.anydatetime("activity_start_time"),
                timezone=self.anytimezone("timezone"),
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
            ).save(session)

        async with self.db_session.begin() as session:
            booking_activity_template = (
                await session.scalars(
                    BookingActivityTemplateOrm.select().where(BookingActivityTemplateOrm.booking_id == booking.id)
                )
            ).one()

            assert booking_activity_template.start_time_utc == self.getdatetime("activity_start_time")
            assert booking_activity_template.start_time_utc.tzinfo == UTC
            assert booking_activity_template.timezone == self.gettimezone("timezone")
            assert booking_activity_template.source == ActivitySource.EVENTBRITE
            assert booking_activity_template.start_time_local == self.getdatetime("activity_start_time").astimezone(
                self.gettimezone("timezone")
            )
