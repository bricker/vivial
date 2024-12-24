from datetime import datetime
from sqlalchemy.dialects.postgresql import Range

from eave.core.lib.address import Address
from eave.core.orm.evergreen_activity import EvergreenActivityOrm, EvergreenActivityTicketTypeOrm, WeeklyScheduleOrm
from eave.core.orm.image import ImageOrm
from eave.core.shared.enums import OutingBudget
from eave.core.shared.geo import GeoPoint
from eave.stdlib.time import LOS_ANGELES_TIMEZONE

from ..base import BaseTestCase


class TestEvergreenActivityOrm(BaseTestCase):
    def make_evergreen_activity(self, session) -> EvergreenActivityOrm:
        activity = EvergreenActivityOrm(
            session,
            title=self.anystr("title"),
            description=self.anystr("description"),
            coordinates=self.anycoordinates(),
            is_bookable=self.anybool("is_bookable"),
            booking_url=self.anyurl("booking_url"),
            activity_category_id=self.anyuuid("category_id"),
            duration_minutes=self.anyint("duration_minutes"),
            address=self.anyaddress(),
            google_place_id=self.anystr(),
        )
        return activity

    async def test_new_activity_record(self) -> None:
        async with self.db_session.begin() as session:
            activity = EvergreenActivityOrm(
                session,
                title=self.anystr("title"),
                description=self.anystr("description"),
                coordinates=GeoPoint(
                    lat=self.anylatitude("lat"),
                    lon=self.anylongitude("lon"),
                ),
                is_bookable=self.anybool("is_bookable"),
                booking_url=self.anyurl("booking_url"),
                activity_category_id=self.anyuuid("category_id"),
                duration_minutes=self.anyint("duration_minutes"),
                google_place_id=self.anystr("google place id"),
                address=Address(
                    address1=self.anystr("address.address1"),
                    address2=self.anystr("address.address2"),
                    city=self.anystr("address.city"),
                    country=self.anystr("address.country"),
                    state=self.anyusstate("address.state"),
                    zip_code=self.anydigits("address.zip", length=5),
                ),
            )

        async with self.db_session.begin() as session:
            obj = await EvergreenActivityOrm.get_one(session, activity.id)

            assert obj.title == self.getstr("title")
            assert obj.description == self.getstr("description")
            assert obj.is_bookable == self.getbool("is_bookable")
            assert obj.booking_url == self.geturl("booking_url")
            assert obj.activity_category_id == self.getuuid("category_id")
            assert obj.duration_minutes == self.getint("duration_minutes")
            assert (
                obj.coordinates
                == GeoPoint(lat=self.getlatitude("lat"), lon=self.getlongitude("lon")).geoalchemy_shape()
            )

            assert obj.address.address1 == self.getstr("address.address1")
            assert obj.address.address2 == self.getstr("address.address2")
            assert obj.address.city == self.getstr("address.city")
            assert obj.address.country == self.getstr("address.country")
            assert obj.address.state == self.getusstate("address.state")
            assert obj.address.zip_code == self.getdigits("address.zip")
            assert obj.google_place_id == self.getstr("google place id")


    async def test_evergreen_activity_select_by_budget_1(self) -> None:
        assert OutingBudget.INEXPENSIVE.upper_limit_cents is not None

        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            EvergreenActivityTicketTypeOrm(
                session,
                evergreen_activity=activity,
                base_cost_cents=OutingBudget.INEXPENSIVE.upper_limit_cents,
                service_fee_cents=10,
                tax_percentage=0.07,
                title=self.anystr(),
            )

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(budget=OutingBudget.MODERATE))).all()

        assert len(results) == 1

    async def test_weekly_schedule_search_1(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            WeeklyScheduleOrm(
                session,
                evergreen_activity=activity,
                week_of=None,
                minute_spans_local=[
                    Range(17*60, 22*60) # monday 17:00-22:00
                ]
            )

        # monday 21:00
        testdate = datetime(2024, 12, 23, 21, 0, tzinfo=LOS_ANGELES_TIMEZONE)

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(open_at_local=testdate))).all()

        assert len(results) == 1

    async def test_weekly_schedule_search_2(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            WeeklyScheduleOrm(
                session,
                evergreen_activity=activity,
                week_of=None,
                minute_spans_local=[
                    Range(21*60, 22*60) # monday 21:00-22:00
                ]
            )

        # monday 21:00
        testdate = datetime(2024, 12, 23, 21, 0, tzinfo=LOS_ANGELES_TIMEZONE)

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(open_at_local=testdate))).all()

        assert len(results) == 1

    async def test_weekly_schedule_search_3(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            WeeklyScheduleOrm(
                session,
                evergreen_activity=activity,
                week_of=None,
                minute_spans_local=[
                    Range(18*60, 22*60) # monday 18:00-22:00
                ]
            )

        # monday 17:00
        testdate = datetime(2024, 12, 23, 17, 0, tzinfo=LOS_ANGELES_TIMEZONE)

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(open_at_local=testdate))).all()

        assert len(results) == 0

    async def test_weekly_schedule_search_4(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            WeeklyScheduleOrm(
                session,
                evergreen_activity=activity,
                week_of=None,
                minute_spans_local=[
                    Range((6*24+18)*60, (6*24+22)*60) # sunday 18:00-22:00
                ]
            )

        # monday 21:00
        testdate = datetime(2024, 12, 23, 17, 0, tzinfo=LOS_ANGELES_TIMEZONE)

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(open_at_local=testdate))).all()

        assert len(results) == 0

    async def test_weekly_schedule_search_5(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            WeeklyScheduleOrm(
                session,
                evergreen_activity=activity,
                week_of=None,
                minute_spans_local=[
                    Range((2*24+18)*60, (3*24+2)*60) # wed 18:00-thu 2:00
                ]
            )

        # wed 21:00
        testdate = datetime(2024, 12, 25, 21, 0, tzinfo=LOS_ANGELES_TIMEZONE)

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(open_at_local=testdate))).all()

        assert len(results) == 1

    async def test_weekly_schedule_search_6(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            WeeklyScheduleOrm(
                session,
                evergreen_activity=activity,
                week_of=None,
                minute_spans_local=[
                    Range((2*24+18)*60, (3*24+2)*60) # wed 18:00-thu 2:00
                ]
            )

        # thu 01:00
        testdate = datetime(2024, 12, 26, 1, 0, tzinfo=LOS_ANGELES_TIMEZONE)

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(open_at_local=testdate))).all()

        assert len(results) == 1

    async def test_weekly_schedule_search_7(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            WeeklyScheduleOrm(
                session,
                evergreen_activity=activity,
                week_of=None,
                minute_spans_local=[
                    Range((2*24+18)*60, (3*24+2)*60) # wed 18:00-thu 2:00
                ]
            )

        # thu 02:00
        testdate = datetime(2024, 12, 26, 2, 0, tzinfo=LOS_ANGELES_TIMEZONE)

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(open_at_local=testdate))).all()

        assert len(results) == 0

    async def test_weekly_schedule_search_8(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            WeeklyScheduleOrm(
                session,
                evergreen_activity=activity,
                week_of=None,
                minute_spans_local=[
                    Range((6*24+18)*60, (7*24)*60) # sun 18:00-mon 00:00
                ]
            )

        # sun 21:00
        testdate = datetime(2024, 12, 22, 21, 0, tzinfo=LOS_ANGELES_TIMEZONE)

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(open_at_local=testdate))).all()

        assert len(results) == 1

    async def test_weekly_schedule_search_9(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            WeeklyScheduleOrm(
                session,
                evergreen_activity=activity,
                week_of=None,
                minute_spans_local=[
                    Range((6*24+18)*60, (7*24)*60) # sun 18:00-mon 00:00
                ]
            )

        # mon 00:00
        testdate = datetime(2024, 12, 23, 0, 0, tzinfo=LOS_ANGELES_TIMEZONE)

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(open_at_local=testdate))).all()

        assert len(results) == 0

    async def test_weekly_schedule_search_10(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            WeeklyScheduleOrm(
                session,
                evergreen_activity=activity,
                week_of=None,
                minute_spans_local=[
                    Range(0, 2*60), # mon 00:00-mon 02:00
                    Range((6*24+18)*60, (7*24)*60) # sun 18:00-mon 00:00
                ]
            )

        # mon 01:00
        testdate = datetime(2024, 12, 23, 1, 0, tzinfo=LOS_ANGELES_TIMEZONE)

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(open_at_local=testdate))).all()

        assert len(results) == 1

    async def test_weekly_schedule_search_11(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            WeeklyScheduleOrm(
                session,
                evergreen_activity=activity,
                week_of=None,
                minute_spans_local=[
                    Range(0, 2*60), # mon 00:00-mon 02:00
                    Range((6*24+18)*60, 7*24*60) # sun 18:00-mon 00:00
                ]
            )

        # mon 02:00
        testdate = datetime(2024, 12, 23, 2, 0, tzinfo=LOS_ANGELES_TIMEZONE)

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(open_at_local=testdate))).all()

        assert len(results) == 0

    async def test_weekly_schedule_search_12(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            WeeklyScheduleOrm(
                session,
                evergreen_activity=activity,
                week_of=None,
                minute_spans_local=[
                    Range(0, 2*60), # mon 00:00-mon 02:00
                    Range((6*24+18)*60, 7*24*60) # sun 18:00-mon 00:00
                ]
            )

        # mon 00:00
        testdate = datetime(2024, 12, 23, 0, 0, tzinfo=LOS_ANGELES_TIMEZONE)

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(open_at_local=testdate))).all()

        assert len(results) == 1

    async def test_activity_images(self) -> None:
        async with self.db_session.begin() as session:
            activity_orm = self.make_evergreen_activity(session)

            images = [
                ImageOrm(
                    session,
                    src=self.anyurl("image src 1"),
                    alt=self.anystr("image alt 1"),
                ),
                ImageOrm(
                    session,
                    src=self.anyurl("image src 2"),
                    alt=self.anystr("image alt 2"),
                ),
            ]

            activity_orm.images = images

        async with self.db_session.begin() as session:
            activity_orm_fetched = await EvergreenActivityOrm.get_one(session, activity_orm.id)
            assert len(activity_orm_fetched.images) == 2

            assert activity_orm_fetched.images[0].src == self.geturl("image src 1")
            assert activity_orm_fetched.images[0].alt == self.geturl("image alt 1")
            assert activity_orm_fetched.images[1].src == self.geturl("image src 2")
            assert activity_orm_fetched.images[1].alt == self.geturl("image alt 2")
