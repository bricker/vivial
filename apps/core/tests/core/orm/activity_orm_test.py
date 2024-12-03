from eave.core.lib.geo import GeoPoint
from eave.core.orm.activity import ActivityOrm
from eave.core.orm.address_types import Address

from ..base import BaseTestCase


class TestActivityOrm(BaseTestCase):
    async def test_new_activity_record(self) -> None:
        async with self.db_session.begin() as session:
            activity = ActivityOrm.build(
                title=self.anystr("title"),
                description=self.anystr("description"),
                lat=self.anylatitude("lat"),
                lon=self.anylongitude("lon"),
                is_bookable=self.anybool("is_bookable"),
                booking_url=self.anyurl("booking_url"),
                subcategory_id=self.anyuuid("subcategory_id"),
                duration_minutes=self.anyint("duration_minutes"),
                availability=self.anystr("availability"),
                address=Address(
                    address1=self.anystr("address.address1"),
                    address2=self.anystr("address.address2"),
                    city=self.anystr("address.city"),
                    country=self.anystr("address.country"),
                    state=self.anyusstate("address.state"),
                    zip=self.anydigits("address.zip"),
                ),
            )
            session.add(activity)

        async with self.db_session.begin() as session:
            obj = await ActivityOrm.get_one(session, activity.id)

            assert obj.title == self.getstr("title")
            assert obj.description == self.getstr("description")
            assert obj.is_bookable == self.getbool("is_bookable")
            assert obj.booking_url == self.geturl("booking_url")
            assert obj.subcategory_id == self.getuuid("subcategory_id")
            assert obj.duration_minutes == self.getint("duration_minutes")
            assert obj.availability == self.getstr("availability")
            assert (
                obj.coordinates
                == GeoPoint(lat=self.getlatitude("lat"), lon=self.getlongitude("lon")).geoalchemy_shape()
            )

            assert obj.address.address1 == self.getstr("address.address1")
            assert obj.address.address2 == self.getstr("address.address2")
            assert obj.address.city == self.getstr("address.city")
            assert obj.address.country == self.getstr("address.country")
            assert obj.address.state == self.getusstate("address.state")
            assert obj.address.zip == self.getdigits("address.zip")
