from eave.core.lib.geo import GeoPoint
from eave.core.orm.activity import ActivityOrm
from eave.core.orm.address_types import PostgisStdaddr

from ..base import BaseTestCase


class TestActivityOrm(BaseTestCase):
    async def test_new_record(self) -> None:
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
                address=PostgisStdaddr(
                    building=self.anystr("addr.building"),
                    house_num=self.anystr("addr.house_num"),
                    predir=self.anystr("addr.predir"),
                    qual=self.anystr("addr.qual"),
                    pretype=self.anystr("addr.pretype"),
                    name=self.anystr("addr.name"),
                    suftype=self.anystr("addr.suftype"),
                    sufdir=self.anystr("addr.sufdir"),
                    ruralroute=self.anystr("addr.ruralroute"),
                    extra=self.anystr("addr.extra"),
                    city=self.anystr("addr.city"),
                    state=self.anystr("addr.state"),
                    country=self.anystr("addr.country"),
                    postcode=self.anystr("addr.postcode"),
                    box=self.anystr("addr.box"),
                    unit=self.anystr("addr.unit"),
                ),
            )
            session.add(activity)

        async with self.db_session.begin() as session:
            obj = (
                await session.scalars(
                    ActivityOrm.select().where(
                        ActivityOrm.id == activity.id,
                    )
                )
            ).one()

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

            assert obj.address.building == self.getstr("addr.building")
            assert obj.address.house_num == self.getstr("addr.house_num")
            assert obj.address.predir == self.getstr("addr.predir")
            assert obj.address.qual == self.getstr("addr.qual")
            assert obj.address.pretype == self.getstr("addr.pretype")
            assert obj.address.name == self.getstr("addr.name")
            assert obj.address.suftype == self.getstr("addr.suftype")
            assert obj.address.sufdir == self.getstr("addr.sufdir")
            assert obj.address.ruralroute == self.getstr("addr.ruralroute")
            assert obj.address.extra == self.getstr("addr.extra")
            assert obj.address.city == self.getstr("addr.city")
            assert obj.address.state == self.getstr("addr.state")
            assert obj.address.country == self.getstr("addr.country")
            assert obj.address.postcode == self.getstr("addr.postcode")
            assert obj.address.box == self.getstr("addr.box")
            assert obj.address.unit == self.getstr("addr.unit")
