import random
from datetime import datetime

from sqlalchemy.dialects.postgresql import Range
from sqlalchemy.ext.asyncio import AsyncSession

from eave.core.lib.address import Address
from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.evergreen_activity import EvergreenActivityOrm, EvergreenActivityTicketTypeOrm, WeeklyScheduleOrm
from eave.core.orm.image import ImageOrm
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.shared.enums import OutingBudget
from eave.core.shared.geo import GeoPoint
from eave.stdlib.time import LOS_ANGELES_TIMEZONE

from ..base import BaseTestCase


class TestEvergreenActivityOrm(BaseTestCase):
    def make_evergreen_activity(self, session: AsyncSession | None = None) -> EvergreenActivityOrm:
        activity = EvergreenActivityOrm(
            session,
            title=self.anystr(),
            description=self.anystr(),
            coordinates=self.anycoordinates(),
            is_bookable=self.anybool(),
            booking_url=self.anyurl(),
            activity_category_id=self.anyuuid(),
            duration_minutes=self.anyint(),
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
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            cost = self.anyint(min=1, max=5) * 100  # INEXPENSIVE
            EvergreenActivityTicketTypeOrm(
                session,
                evergreen_activity=activity,
                min_base_cost_cents=cost,
                max_base_cost_cents=cost,
                service_fee_cents=self.anyint(min=0, max=10) * 100,
                tax_percentage=self.anyint(min=0, max=7) / 100,
                title=self.anystr(),
            )

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(budget=OutingBudget.MODERATE))).all()

        assert len(results) == 1

    async def test_evergreen_activity_select_by_budget_2(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            cost = self.anyint(min=10**6) * 100  # VERY EXPENSIVE
            EvergreenActivityTicketTypeOrm(
                session,
                evergreen_activity=activity,
                min_base_cost_cents=cost,
                max_base_cost_cents=cost,
                service_fee_cents=self.anyint(),
                tax_percentage=self.anyfloat(),
                title=self.anystr(),
            )

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(budget=OutingBudget.MODERATE))).all()

        assert len(results) == 0

    async def test_evergreen_activity_select_by_budget_3(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            cost = self.anyint(min=11, max=100) * 100  # within MODERATE
            EvergreenActivityTicketTypeOrm(
                session,
                evergreen_activity=activity,
                min_base_cost_cents=cost,
                max_base_cost_cents=cost,
                service_fee_cents=self.anyint(min=0, max=10) * 100,
                tax_percentage=self.anyint(min=0, max=10) / 100,
                title=self.anystr(),
            )

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(budget=OutingBudget.INEXPENSIVE))).all()

        assert len(results) == 0

    async def test_evergreen_activity_select_by_budget_5(self) -> None:
        assert OutingBudget.MODERATE.upper_limit_cents is not None

        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            cost = self.anyint(min=10**6) * 100
            EvergreenActivityTicketTypeOrm(
                session,
                evergreen_activity=activity,
                min_base_cost_cents=cost,
                max_base_cost_cents=cost,
                service_fee_cents=self.anyint(min=0, max=5) * 100,
                tax_percentage=0.07,
                title=self.anystr(),
            )

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(budget=OutingBudget.VERY_EXPENSIVE))).all()

        assert len(results) == 1

    async def test_evergreen_activity_select_by_budget_4(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            EvergreenActivityTicketTypeOrm(
                session,
                evergreen_activity=activity,
                min_base_cost_cents=40 * 100,
                max_base_cost_cents=40 * 100,  # MODERATE is 50 bucks max
                service_fee_cents=5 * 100,
                tax_percentage=20 / 100,  # result is $54, above MODERATE limit
                title=self.anystr(),
            )

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(budget=OutingBudget.MODERATE))).all()

        assert len(results) == 0

    async def test_evergreen_activity_select_by_budget_6(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            EvergreenActivityTicketTypeOrm(
                session,
                evergreen_activity=activity,
                max_base_cost_cents=0,
                min_base_cost_cents=0,
                service_fee_cents=0,
                tax_percentage=0,
                title=self.anystr(),
            )

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(budget=OutingBudget.INEXPENSIVE))).all()

        assert len(results) == 1

    async def test_evergreen_activity_select_by_budget_7(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            EvergreenActivityTicketTypeOrm(
                session,
                evergreen_activity=activity,
                max_base_cost_cents=0,
                min_base_cost_cents=0,
                service_fee_cents=0,
                tax_percentage=0,
                title=self.anystr(),
            )

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(budget=OutingBudget.FREE))).all()

        assert len(results) == 1

    async def test_evergreen_activity_select_by_budget_8(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            EvergreenActivityTicketTypeOrm(
                session,
                evergreen_activity=activity,
                max_base_cost_cents=0,
                min_base_cost_cents=0,
                service_fee_cents=0,
                tax_percentage=0,
                title=self.anystr(),
            )

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(budget=OutingBudget.FREE))).all()

        assert len(results) == 1

    async def test_evergreen_activity_select_by_budget_9(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            EvergreenActivityTicketTypeOrm(
                session,
                evergreen_activity=activity,
                max_base_cost_cents=0,
                min_base_cost_cents=0,
                service_fee_cents=0,
                tax_percentage=0,
                title=self.anystr(),
            )

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(budget=OutingBudget.VERY_EXPENSIVE))).all()

        assert len(results) == 1

    async def test_evergreen_activity_select_by_budget_10(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            cost = self.anyint(min=10**6) * 100
            EvergreenActivityTicketTypeOrm(
                session,
                evergreen_activity=activity,
                max_base_cost_cents=cost,
                min_base_cost_cents=cost,
                service_fee_cents=0,
                tax_percentage=0,
                title=self.anystr(),
            )

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(budget=OutingBudget.FREE))).all()

        assert len(results) == 0

    async def test_evergreen_activity_select_by_budget_11(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            EvergreenActivityTicketTypeOrm(
                session,
                evergreen_activity=activity,
                max_base_cost_cents=150 * 100,  # EXPENSIVE upper bound
                min_base_cost_cents=150 * 100,
                service_fee_cents=self.anyint(min=1, max=10) * 100,
                tax_percentage=self.anyint(min=0, max=10) / 100,
                title=self.anystr(),
            )

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(budget=OutingBudget.EXPENSIVE))).all()

        assert len(results) == 0

    async def test_evergreen_activity_select_by_budget_12(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            EvergreenActivityTicketTypeOrm(
                session,
                evergreen_activity=activity,
                max_base_cost_cents=150 * 100,  # EXPENSIVE upper bound
                min_base_cost_cents=150 * 100,
                service_fee_cents=0,
                tax_percentage=0,
                title=self.anystr(),
            )

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(budget=OutingBudget.EXPENSIVE))).all()

        assert len(results) == 1

    async def test_evergreen_activity_select_by_budget_13(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)

            for cost in [
                (150, 0, 0),
                (150, self.anyint(min=1, max=10), self.anyint(min=0, max=10)),
                (self.anyint(min=10**6), self.anyint(min=0, max=10), self.anyint(min=0, max=10)),
            ]:
                EvergreenActivityTicketTypeOrm(
                    session,
                    evergreen_activity=activity,
                    max_base_cost_cents=cost[0] * 100,
                    min_base_cost_cents=cost[0] * 100,
                    service_fee_cents=cost[1] * 100,
                    tax_percentage=cost[2] / 100,
                    title=self.anystr(),
                )

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(budget=OutingBudget.EXPENSIVE))).all()

        assert len(results) == 1

    async def test_evergreen_activity_select_by_budget_13_5(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)

            for cost in [
                (self.anyint(min=200), 0, 0),
                (self.anyint(min=300), self.anyint(min=1, max=10), self.anyint(min=0, max=10)),
                (self.anyint(min=10**6), self.anyint(min=0, max=10), self.anyint(min=0, max=10)),
            ]:
                EvergreenActivityTicketTypeOrm(
                    session,
                    evergreen_activity=activity,
                    max_base_cost_cents=cost[0] * 100,
                    min_base_cost_cents=cost[0] * 100,
                    service_fee_cents=cost[1] * 100,
                    tax_percentage=cost[2] / 100,
                    title=self.anystr(),
                )

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(budget=OutingBudget.EXPENSIVE))).all()

        assert len(results) == 0

    async def test_evergreen_activity_select_by_budget_14(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)

            for cost in [
                (self.anyint(max=100), 0, 0),
                (150, self.anyint(min=1, max=10), self.anyint(min=0, max=10)),
                (self.anyint(min=10**6), self.anyint(min=0, max=10), self.anyint(min=0, max=10)),
            ]:
                EvergreenActivityTicketTypeOrm(
                    session,
                    evergreen_activity=activity,
                    max_base_cost_cents=cost[0] * 100,
                    min_base_cost_cents=cost[0] * 100,
                    service_fee_cents=cost[1] * 100,
                    tax_percentage=cost[2] / 100,
                    title=self.anystr(),
                )

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(budget=OutingBudget.EXPENSIVE))).all()

        assert len(results) == 1

    async def test_evergreen_activity_select_by_budget_15(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)

            for cost in [
                (self.anyint(max=100), 0, 0),
                (self.anyint(max=50), self.anyint(min=1, max=10), self.anyint(min=0, max=10)),
                (self.anyint(min=10**6), self.anyint(min=0, max=10), self.anyint(min=0, max=10)),
            ]:
                EvergreenActivityTicketTypeOrm(
                    session,
                    evergreen_activity=activity,
                    max_base_cost_cents=cost[0] * 100,
                    min_base_cost_cents=cost[0] * 100,
                    service_fee_cents=cost[1] * 100,
                    tax_percentage=cost[2] / 100,
                    title=self.anystr(),
                )

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(budget=OutingBudget.EXPENSIVE))).all()

        assert len(results) == 1

    async def test_evergreen_activity_select_by_budget_16(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)

            for cost in [(0, 0, 0), (1, 0, 0), (self.anyint(max=-1), self.anyint(max=-1), self.anyint(max=-10))]:
                EvergreenActivityTicketTypeOrm(
                    session,
                    evergreen_activity=activity,
                    max_base_cost_cents=cost[0] * 100,
                    min_base_cost_cents=cost[0] * 100,
                    service_fee_cents=cost[1] * 100,
                    tax_percentage=cost[2] / 100,
                    title=self.anystr(),
                )

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(budget=OutingBudget.EXPENSIVE))).all()

        assert len(results) == 1

    async def test_evergreen_activity_select_by_budget_17(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)

            for cost in [
                (0, 0, 0),
                (self.anyint(max=20), self.anyint(max=10), self.anyint(max=20)),
                (self.anyint(min=10**6), self.anyint(max=10), self.anyint(max=20)),
            ]:
                EvergreenActivityTicketTypeOrm(
                    session,
                    evergreen_activity=activity,
                    max_base_cost_cents=cost[0] * 100,
                    min_base_cost_cents=cost[0] * 100,
                    service_fee_cents=cost[1] * 100,
                    tax_percentage=cost[2] / 100,
                    title=self.anystr(),
                )

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(budget=OutingBudget.VERY_EXPENSIVE))).all()

        assert len(results) == 1

    async def test_evergreen_activity_select_by_budget_18(self) -> None:
        async with self.db_session.begin() as session:
            activity_1 = self.make_evergreen_activity(session)
            activity_2 = self.make_evergreen_activity(session)

            EvergreenActivityTicketTypeOrm(
                session,
                evergreen_activity=activity_1,
                max_base_cost_cents=20 * 100,
                min_base_cost_cents=20 * 100,
                service_fee_cents=0,
                tax_percentage=0,
                title=self.anystr(),
            )

            EvergreenActivityTicketTypeOrm(
                session,
                evergreen_activity=activity_2,
                max_base_cost_cents=5 * 100,
                min_base_cost_cents=5 * 100,
                service_fee_cents=0,
                tax_percentage=0,
                title=self.anystr(),
            )

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(budget=OutingBudget.INEXPENSIVE))).all()

        assert len(results) == 1
        assert results[0].id == activity_2.id

    async def test_evergreen_activity_select_by_budget_19(self) -> None:
        async with self.db_session.begin() as session:
            activity_1 = self.make_evergreen_activity(session)
            activity_2 = self.make_evergreen_activity(session)
            activity_3 = self.make_evergreen_activity(session)

            EvergreenActivityTicketTypeOrm(
                session,
                evergreen_activity=activity_1,
                max_base_cost_cents=20 * 100,
                min_base_cost_cents=20 * 100,
                service_fee_cents=0,
                tax_percentage=0,
                title=self.anystr(),
            )

            EvergreenActivityTicketTypeOrm(
                session,
                evergreen_activity=activity_2,
                max_base_cost_cents=5 * 100,
                min_base_cost_cents=5 * 100,
                service_fee_cents=0,
                tax_percentage=0,
                title=self.anystr(),
            )

            EvergreenActivityTicketTypeOrm(
                session,
                evergreen_activity=activity_3,
                max_base_cost_cents=7 * 100,
                min_base_cost_cents=7 * 100,
                service_fee_cents=0,
                tax_percentage=0,
                title=self.anystr(),
            )

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(budget=OutingBudget.INEXPENSIVE))).all()

        assert len(results) == 2
        assert results[0].id == activity_2.id
        assert results[1].id == activity_3.id

    async def test_weekly_schedule_search_1(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            WeeklyScheduleOrm(
                session,
                evergreen_activity=activity,
                week_of=None,
                minute_spans_local=[
                    Range(17 * 60, 22 * 60)  # monday 17:00-22:00
                ],
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
                    Range(21 * 60, 22 * 60)  # monday 21:00-22:00
                ],
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
                    Range(18 * 60, 22 * 60)  # monday 18:00-22:00
                ],
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
                    Range((6 * 24 + 18) * 60, (6 * 24 + 22) * 60)  # sunday 18:00-22:00
                ],
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
                    Range((2 * 24 + 18) * 60, (3 * 24 + 2) * 60)  # wed 18:00-thu 2:00
                ],
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
                    Range((2 * 24 + 18) * 60, (3 * 24 + 2) * 60)  # wed 18:00-thu 2:00
                ],
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
                    Range((2 * 24 + 18) * 60, (3 * 24 + 2) * 60)  # wed 18:00-thu 2:00
                ],
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
                    Range((6 * 24 + 18) * 60, (7 * 24) * 60)  # sun 18:00-mon 00:00
                ],
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
                    Range((6 * 24 + 18) * 60, (7 * 24) * 60)  # sun 18:00-mon 00:00
                ],
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
                    Range(0, 2 * 60),  # mon 00:00-mon 02:00
                    Range((6 * 24 + 18) * 60, (7 * 24) * 60),  # sun 18:00-mon 00:00
                ],
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
                    Range(0, 2 * 60),  # mon 00:00-mon 02:00
                    Range((6 * 24 + 18) * 60, 7 * 24 * 60),  # sun 18:00-mon 00:00
                ],
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
                    Range(0, 2 * 60),  # mon 00:00-mon 02:00
                    Range((6 * 24 + 18) * 60, 7 * 24 * 60),  # sun 18:00-mon 00:00
                ],
            )

        # mon 00:00
        testdate = datetime(2024, 12, 23, 0, 0, tzinfo=LOS_ANGELES_TIMEZONE)

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(open_at_local=testdate))).all()

        assert len(results) == 1

    async def test_weekly_schedule_search_13(self) -> None:
        async with self.db_session.begin() as session:
            activity_1 = self.make_evergreen_activity(session)
            WeeklyScheduleOrm(
                session,
                evergreen_activity=activity_1,
                week_of=None,
                minute_spans_local=[
                    Range((5 * 24 + 18) * 60, (6 * 24 + 2) * 60)  # sat 18:00-sun 02:00
                ],
            )

            activity_2 = self.make_evergreen_activity(session)
            WeeklyScheduleOrm(
                session,
                evergreen_activity=activity_2,
                week_of=None,
                minute_spans_local=[
                    Range((5 * 24 + 12) * 60, (5 * 24 + 22) * 60)  # sat 12:00-sat 22:00
                ],
            )

            activity_3 = self.make_evergreen_activity(session)
            WeeklyScheduleOrm(
                session,
                evergreen_activity=activity_3,
                week_of=None,
                minute_spans_local=[
                    Range((5 * 24 + 8) * 60, (5 * 24 + 14) * 60)  # sat 08:00-sat 14:00
                ],
            )

        # sat 21:00
        testdate = datetime(2024, 12, 21, 21, 0, tzinfo=LOS_ANGELES_TIMEZONE)

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(open_at_local=testdate))).all()

        assert len(results) == 2

    async def test_evergreen_activity_seach_by_category_ids_1(self) -> None:
        category_id = random.choice(ActivityCategoryOrm.all()).id

        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            activity.activity_category_id = category_id

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(activity_category_ids=[category_id]))).all()

        assert len(results) == 1

    async def test_evergreen_activity_seach_by_category_ids_2(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            activity.activity_category_id = ActivityCategoryOrm.all()[0].id

            activity2 = self.make_evergreen_activity(session)
            activity2.activity_category_id = ActivityCategoryOrm.all()[0].id

            activity3 = self.make_evergreen_activity(session)
            activity3.activity_category_id = ActivityCategoryOrm.all()[1].id

        async with self.db_session.begin() as session:
            results = (
                await session.scalars(
                    EvergreenActivityOrm.select(activity_category_ids=[ActivityCategoryOrm.all()[0].id])
                )
            ).all()

        assert len(results) == 2

    async def test_evergreen_activity_seach_by_category_ids_3(self) -> None:
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            activity.activity_category_id = ActivityCategoryOrm.all()[0].id

            activity2 = self.make_evergreen_activity(session)
            activity2.activity_category_id = ActivityCategoryOrm.all()[1].id

            activity3 = self.make_evergreen_activity(session)
            activity3.activity_category_id = ActivityCategoryOrm.all()[2].id

        async with self.db_session.begin() as session:
            results = (
                await session.scalars(
                    EvergreenActivityOrm.select(
                        activity_category_ids=[
                            ActivityCategoryOrm.all()[0].id,
                            ActivityCategoryOrm.all()[1].id,
                            ActivityCategoryOrm.all()[2].id,
                        ]
                    )
                )
            ).all()

        assert len(results) == 3

    async def test_evergreen_activity_seach_by_areas_1(self) -> None:
        region = random.choice(SearchRegionOrm.all())

        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            activity.coordinates = region.area.center.geoalchemy_shape()

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(within_areas=[region.area]))).all()

        assert len(results) == 1

    async def test_evergreen_activity_seach_by_areas_2(self) -> None:
        region = random.choice(SearchRegionOrm.all())
        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            activity.coordinates = GeoPoint(
                lat=region.area.center.lat
                + 0.0001,  # This is janky but the point is to test a venue not at the center of the area, and adding 0.0001 is unlikely to fall outside of the area.
                lon=region.area.center.lon + 0.0001,
            ).geoalchemy_shape()

        async with self.db_session.begin() as session:
            results = (await session.scalars(EvergreenActivityOrm.select(within_areas=[region.area]))).all()

        assert len(results) == 1

    async def test_evergreen_activity_seach_by_areas_overlapping(self) -> None:
        # These two regions overlap. The center of the Downtown LA region is within the bounds of the Central LA region.
        central_la = SearchRegionOrm.all()[0]
        dtla = SearchRegionOrm.all()[1]

        # This one doesn't overlap, used as control
        glendale = SearchRegionOrm.all()[2]  # Downtown LA

        async with self.db_session.begin() as session:
            activity_1 = self.make_evergreen_activity(session)
            activity_1.coordinates = central_la.area.center.geoalchemy_shape()

            activity_2 = self.make_evergreen_activity(session)
            activity_2.coordinates = dtla.area.center.geoalchemy_shape()

            activity_3 = self.make_evergreen_activity(session)
            activity_3.coordinates = glendale.area.center.geoalchemy_shape()

        async with self.db_session.begin() as session:
            results_1 = (await session.scalars(EvergreenActivityOrm.select(within_areas=[central_la.area]))).all()
            results_2 = (await session.scalars(EvergreenActivityOrm.select(within_areas=[dtla.area]))).all()
            results_3 = (
                await session.scalars(EvergreenActivityOrm.select(within_areas=[central_la.area, dtla.area]))
            ).all()
            results_4 = (await session.scalars(EvergreenActivityOrm.select(within_areas=[glendale.area]))).all()
            results_5 = (
                await session.scalars(
                    EvergreenActivityOrm.select(within_areas=[central_la.area, dtla.area, glendale.area])
                )
            ).all()

        assert len(results_1) == 2  # because DTLA is within Central LA regions
        assert results_1[0].id == activity_1.id
        assert results_1[1].id == activity_2.id

        assert len(results_2) == 1  # Because the center of Central LA region isn't within the DTLA region
        assert results_2[0].id == activity_2.id

        assert len(results_3) == 2
        assert results_1[0].id == activity_1.id
        assert results_1[1].id == activity_2.id

        assert len(results_4) == 1
        assert results_4[0].id == activity_3.id

        assert len(results_5) == 3
        assert results_5[0].id == activity_1.id
        assert results_5[1].id == activity_2.id
        assert results_5[2].id == activity_3.id

    async def test_evergreen_search_multiple_conditions_1(self) -> None:
        region = random.choice(SearchRegionOrm.all())
        category = random.choice(ActivityCategoryOrm.all())

        async with self.db_session.begin() as session:
            activity = self.make_evergreen_activity(session)
            activity.coordinates = region.area.center.geoalchemy_shape()
            activity.activity_category_id = category.id
            WeeklyScheduleOrm(
                session,
                evergreen_activity=activity,
                week_of=None,
                minute_spans_local=[
                    Range((2 * 24 + 18) * 60, (3 * 24 + 2) * 60)  # wed 18:00-thu 2:00
                ],
            )

            cost = self.anyint(max=100)
            EvergreenActivityTicketTypeOrm(
                session,
                evergreen_activity=activity,
                max_base_cost_cents=cost,
                min_base_cost_cents=cost,
                service_fee_cents=self.anyint(max=100),
                tax_percentage=self.anyint(max=2) / 100,
                title=self.anystr(),
            )

        # wed 21:00
        testdate = datetime(2024, 12, 25, 21)

        async with self.db_session.begin() as session:
            results = (
                await session.scalars(
                    EvergreenActivityOrm.select(
                        within_areas=[region.area],
                        activity_category_ids=[category.id],
                        budget=OutingBudget.EXPENSIVE,
                        open_at_local=testdate,
                    )
                )
            ).all()

        assert len(results) == 1

    async def test_evergreen_search_multiple_conditions_2(self) -> None:
        region_1 = SearchRegionOrm.all()[0]
        region_2 = SearchRegionOrm.all()[1]

        category_1 = ActivityCategoryOrm.all()[0]
        category_2 = ActivityCategoryOrm.all()[1]

        async with self.db_session.begin() as session:
            activity_1 = self.make_evergreen_activity(session)
            activity_1.coordinates = region_1.area.center.geoalchemy_shape()
            activity_1.activity_category_id = category_1.id
            WeeklyScheduleOrm(
                session,
                evergreen_activity=activity_1,
                week_of=None,
                minute_spans_local=[
                    Range((2 * 24 + 18) * 60, (3 * 24 + 2) * 60)  # wed 18:00-thu 2:00
                ],
            )
            cost = self.anyint(max=100)
            EvergreenActivityTicketTypeOrm(
                session,
                evergreen_activity=activity_1,
                max_base_cost_cents=cost,
                min_base_cost_cents=cost,
                service_fee_cents=self.anyint(max=100),
                tax_percentage=self.anyint(max=2) / 100,
                title=self.anystr(),
            )

            activity_2 = self.make_evergreen_activity(session)
            activity_2.coordinates = region_2.area.center.geoalchemy_shape()
            activity_2.activity_category_id = category_2.id
            WeeklyScheduleOrm(
                session,
                evergreen_activity=activity_2,
                week_of=None,
                minute_spans_local=[
                    Range((2 * 24 + 18) * 60, (3 * 24 + 2) * 60)  # wed 18:00-thu 2:00
                ],
            )
            cost = self.anyint(max=100)
            EvergreenActivityTicketTypeOrm(
                session,
                evergreen_activity=activity_2,
                max_base_cost_cents=cost,
                min_base_cost_cents=cost,
                service_fee_cents=self.anyint(max=100),
                tax_percentage=self.anyint(max=2) / 100,
                title=self.anystr(),
            )

        # wed 21:00
        testdate = datetime(2024, 12, 25, 21)

        async with self.db_session.begin() as session:
            results_1 = (
                await session.scalars(
                    EvergreenActivityOrm.select(
                        within_areas=[region_1.area, region_2.area],
                        activity_category_ids=[category_1.id],
                        budget=OutingBudget.EXPENSIVE,
                        open_at_local=testdate,
                    )
                )
            ).all()
            results_2 = (
                await session.scalars(
                    EvergreenActivityOrm.select(
                        within_areas=[region_1.area, region_2.area],
                        budget=OutingBudget.EXPENSIVE,
                        open_at_local=testdate,
                    )
                )
            ).all()

        assert len(results_1) == 1  # Because activity category id for activity 2 not included in query
        assert len(results_2) == 2  # Because activity category id not queried

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

    async def test_ticket_type_total_cost_cents_1(self) -> None:
        activity = self.make_evergreen_activity(None)
        ticket = EvergreenActivityTicketTypeOrm(
            None,
            evergreen_activity=activity,
            max_base_cost_cents=100,
            min_base_cost_cents=100,
            service_fee_cents=5,
            tax_percentage=0.07,
            title=self.anystr(),
        )

        assert ticket.total_cost_cents == 112

    async def test_ticket_type_total_cost_cents_2(self) -> None:
        activity = self.make_evergreen_activity(None)
        ticket = EvergreenActivityTicketTypeOrm(
            None,
            evergreen_activity=activity,
            max_base_cost_cents=100,
            min_base_cost_cents=100,
            service_fee_cents=6,
            tax_percentage=0.07,
            title=self.anystr(),
        )

        assert ticket.total_cost_cents == 113

    async def test_ticket_type_total_cost_cents_3(self) -> None:
        activity = self.make_evergreen_activity(None)
        ticket = EvergreenActivityTicketTypeOrm(
            None,
            evergreen_activity=activity,
            max_base_cost_cents=100,
            min_base_cost_cents=100,
            service_fee_cents=8,
            tax_percentage=0.07,  # This creates 115.56
            title=self.anystr(),
        )

        assert ticket.total_cost_cents == 115  # Floor

    async def test_ticket_type_total_cost_cents_4(self) -> None:
        activity = self.make_evergreen_activity(None)
        ticket = EvergreenActivityTicketTypeOrm(
            None,
            evergreen_activity=activity,
            max_base_cost_cents=1550,
            min_base_cost_cents=1550,
            service_fee_cents=400,
            tax_percentage=0.07,
            title=self.anystr(),
        )

        assert ticket.total_cost_cents == 2086

    async def test_ticket_type_total_cost_cents_5(self) -> None:
        activity = self.make_evergreen_activity(None)
        ticket = EvergreenActivityTicketTypeOrm(
            None,
            evergreen_activity=activity,
            min_base_cost_cents=1550,
            max_base_cost_cents=1550,
            service_fee_cents=400,
            tax_percentage=0.07,
            title=self.anystr(),
        )

        assert ticket.total_cost_cents == 2086
