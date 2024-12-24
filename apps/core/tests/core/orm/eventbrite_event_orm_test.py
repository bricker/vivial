import random
from collections.abc import Sequence
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.eventbrite_event import EventbriteEventOrm
from eave.core.shared.enums import OutingBudget
from eave.core.shared.geo import Distance, GeoArea, GeoPoint
from eave.stdlib.time import ONE_DAY_IN_SECONDS

from ..base import BaseTestCase


class TestEventbriteEventOrm(BaseTestCase):
    def make_eventbrite_event_orm(self, session: AsyncSession) -> EventbriteEventOrm:
        return EventbriteEventOrm(
            session,
            eventbrite_event_id=self.anystr("eventbrite_event_id"),
            eventbrite_organizer_id=self.anystr("eventbrite_organizer_id"),
            title=self.anystr(),
            google_place_id=self.anystr(),
            vivial_activity_category_id=self.anyuuid(),
            vivial_activity_format_id=self.anyuuid(),
            start_time=self.anydatetime("start_time", past=True),
            end_time=self.anydatetime("end_time", future=True),
            timezone=self.anytimezone(),
            min_cost_cents=self.anyint("min_cost", min=0, max=999),
            max_cost_cents=self.anyint("max_cost", min=1000, max=9999),
            lat=self.anylatitude("lat"),
            lon=self.anylongitude("lon"),
        )

    async def test_eventbrite_event_new_event_record(self) -> None:
        async with self.db_session.begin() as session:
            obj = EventbriteEventOrm(
                session,
                eventbrite_event_id=self.anystr("eventbrite_event_id"),
                eventbrite_organizer_id=self.anystr("eventbrite_organizer_id"),
                title=self.anystr(),
                google_place_id=None,
                vivial_activity_category_id=self.anyuuid(),
                vivial_activity_format_id=self.anyuuid(),
                start_time=self.anydatetime("start_time", past=True),
                end_time=self.anydatetime("end_time", future=True),
                timezone=self.anytimezone("timezone"),
                min_cost_cents=self.anyint("min_cost", min=0, max=999),
                max_cost_cents=self.anyint("max_cost", min=1000, max=9999),
                lat=self.anylatitude("lat"),
                lon=self.anylongitude("lon"),
            )

        async with self.db_session.begin() as session:
            obj = (
                await session.scalars(
                    EventbriteEventOrm.select(
                        eventbrite_event_id=self.getstr("eventbrite_event_id"),
                    )
                )
            ).one()

            assert obj.eventbrite_event_id == self.getstr("eventbrite_event_id")
            assert obj.eventbrite_organizer_id == self.getstr("eventbrite_organizer_id")
            assert obj.start_time_utc == self.getdatetime("start_time")
            assert obj.end_time_utc == self.getdatetime("end_time")
            assert obj.max_cost_cents == self.getint("max_cost")
            assert obj.timezone == self.gettimezone("timezone")

    async def test_eventbrite_event_query_budget_1(self) -> None:
        async with self.db_session.begin() as session:
            obj = self.make_eventbrite_event_orm(session)
            obj.max_cost_cents = OutingBudget.EXPENSIVE.upper_limit_cents  # Matches upper limit exactly
            obj.min_cost_cents = 0

        async with self.db_session.begin() as session:
            results = (
                await session.scalars(
                    EventbriteEventOrm.select(budget=OutingBudget.EXPENSIVE),
                )
            ).all()

            assert len(results) == 1

    async def test_eventbrite_event_query_budget_2(self) -> None:
        assert OutingBudget.EXPENSIVE.upper_limit_cents is not None # for typechecker

        async with self.db_session.begin() as session:
            obj = self.make_eventbrite_event_orm(session)
            obj.max_cost_cents = OutingBudget.EXPENSIVE.upper_limit_cents + 100  # max cost above the budget
            obj.min_cost_cents = 0

        async with self.db_session.begin() as session:
            results = (await session.scalars(EventbriteEventOrm.select(budget=OutingBudget.EXPENSIVE))).all()

            assert len(results) == 1

    async def test_eventbrite_event_query_budget_3(self) -> None:
        assert OutingBudget.EXPENSIVE.upper_limit_cents is not None # for typechecker

        async with self.db_session.begin() as session:
            obj = self.make_eventbrite_event_orm(session)
            obj.max_cost_cents = OutingBudget.EXPENSIVE.upper_limit_cents - 100  # max cost below the budget
            obj.min_cost_cents = 0

        async with self.db_session.begin() as session:
            results = (await session.scalars(EventbriteEventOrm.select(budget=OutingBudget.EXPENSIVE))).all()

            assert len(results) == 1

    async def test_eventbrite_event_query_budget_3_1(self) -> None:
        async with self.db_session.begin() as session:
            obj = self.make_eventbrite_event_orm(session)
            obj.max_cost_cents = OutingBudget.MODERATE.upper_limit_cents  # max cost below the budget
            obj.min_cost_cents = 0

        async with self.db_session.begin() as session:
            results = (await session.scalars(EventbriteEventOrm.select(budget=OutingBudget.EXPENSIVE))).all()

            assert len(results) == 1

    async def test_eventbrite_event_query_budget_4(self) -> None:
        async with self.db_session.begin() as session:
            obj = self.make_eventbrite_event_orm(session)
            obj.max_cost_cents = OutingBudget.VERY_EXPENSIVE.upper_limit_cents
            obj.min_cost_cents = OutingBudget.MODERATE.upper_limit_cents  # Min cost below budget max

        async with self.db_session.begin() as session:
            results = (await session.scalars(EventbriteEventOrm.select(budget=OutingBudget.EXPENSIVE))).all()

            assert len(results) == 1

    async def test_eventbrite_event_query_budget_5(self) -> None:
        async with self.db_session.begin() as session:
            obj = self.make_eventbrite_event_orm(session)
            obj.max_cost_cents = OutingBudget.MODERATE.upper_limit_cents
            obj.min_cost_cents = OutingBudget.INEXPENSIVE.upper_limit_cents

        async with self.db_session.begin() as session:
            results = (await session.scalars(EventbriteEventOrm.select(budget=OutingBudget.EXPENSIVE))).all()

            assert len(results) == 1

    async def test_eventbrite_event_query_budget_6(self) -> None:
        async with self.db_session.begin() as session:
            obj = self.make_eventbrite_event_orm(session)
            obj.max_cost_cents = OutingBudget.VERY_EXPENSIVE.upper_limit_cents
            obj.min_cost_cents = OutingBudget.EXPENSIVE.upper_limit_cents  # Exact budget match

        async with self.db_session.begin() as session:
            results = (await session.scalars(EventbriteEventOrm.select(budget=OutingBudget.EXPENSIVE))).all()

            assert len(results) == 1

    async def test_eventbrite_event_query_budget_7(self) -> None:
        async with self.db_session.begin() as session:
            obj = self.make_eventbrite_event_orm(session)
            obj.max_cost_cents = OutingBudget.VERY_EXPENSIVE.upper_limit_cents
            obj.min_cost_cents = OutingBudget.EXPENSIVE.upper_limit_cents  # above budget

        async with self.db_session.begin() as session:
            results = (await session.scalars(EventbriteEventOrm.select(budget=OutingBudget.MODERATE))).all()

            assert len(results) == 0

    async def test_eventbrite_event_query_budget_8(self) -> None:
        async with self.db_session.begin() as session:
            obj = self.make_eventbrite_event_orm(session)
            obj.max_cost_cents = 0
            obj.min_cost_cents = 0

        async with self.db_session.begin() as session:
            results = (await session.scalars(EventbriteEventOrm.select(budget=OutingBudget.MODERATE))).all()

            assert len(results) == 1

    async def test_eventbrite_event_query_budget_9(self) -> None:
        async with self.db_session.begin() as session:
            obj = self.make_eventbrite_event_orm(session)
            obj.max_cost_cents = OutingBudget.EXPENSIVE.upper_limit_cents
            obj.min_cost_cents = OutingBudget.MODERATE.upper_limit_cents

        async with self.db_session.begin() as session:
            results = (await session.scalars(EventbriteEventOrm.select(budget=OutingBudget.FREE))).all()

            assert len(results) == 0

    async def _setup_results(self, start_time: datetime, delta: timedelta) -> Sequence[EventbriteEventOrm]:
        async with self.db_session.begin() as session:
            EventbriteEventOrm(
                session,
                eventbrite_event_id=self.anystr(),
                eventbrite_organizer_id=self.anystr(),
                title=self.anystr(),
                google_place_id=None,
                vivial_activity_category_id=self.anyuuid(),
                vivial_activity_format_id=self.anyuuid(),
                start_time=start_time,
                end_time=start_time + timedelta(minutes=self.anyint(min=15, max=120)),
                timezone=self.anytimezone(),
                min_cost_cents=self.anyint(min=0, max=1999),
                max_cost_cents=self.anyint(min=2000, max=9999),
                lat=self.anylatitude(),
                lon=self.anylongitude(),
            )

        async with self.db_session.begin() as session:
            results = (
                await session.scalars(
                    EventbriteEventOrm.select(
                        start_time=start_time + delta,
                    )
                )
            ).all()

        return results

    async def test_eventbrite_event_query_start_time_20(self) -> None:
        results = await self._setup_results(
            self.anydatetime("start_time", future=True),
            timedelta(minutes=-120),
        )
        assert len(results) == 0

    async def test_eventbrite_event_query_start_time_21(self) -> None:
        results = await self._setup_results(
            self.anydatetime("start_time", future=True), timedelta(minutes=120)
        )
        assert len(results) == 0

    async def test_eventbrite_event_query_start_time_22(self) -> None:
        results = await self._setup_results(
            self.anydatetime("start_time", future=True), timedelta(minutes=0)
        )
        assert len(results) == 1

    async def test_eventbrite_event_query_start_time_22_5(self) -> None:
        results = await self._setup_results(
            self.anydatetime("start_time", future=True), timedelta(minutes=16)
        )
        assert len(results) == 0

    async def test_eventbrite_event_query_start_time_23(self) -> None:
        results = await self._setup_results(
            self.anydatetime("start_time", future=True), timedelta(minutes=-16)
        )
        assert len(results) == 0

    async def test_eventbrite_event_query_start_time_1(self) -> None:
        results = await self._setup_results(datetime(2024, 12, 18, 10, 00), timedelta(minutes=45))
        assert len(results) == 0

    async def test_eventbrite_event_query_start_time_2(self) -> None:
        results = await self._setup_results(datetime(2024, 12, 18, 10, 00), timedelta(minutes=10))
        assert len(results) == 1

    async def test_eventbrite_event_query_start_time_3(self) -> None:
        results = await self._setup_results(datetime(2024, 12, 18, 10, 00), timedelta(minutes=-5))
        assert len(results) == 0

    async def test_eventbrite_event_query_start_time_3_5(self) -> None:
        results = await self._setup_results(datetime(2024, 12, 18, 9, 59), timedelta(minutes=-5))
        assert len(results) == 1

    async def test_eventbrite_event_query_start_time_4(self) -> None:
        results = await self._setup_results(datetime(2024, 12, 18, 10, 10), timedelta(minutes=5))
        assert len(results) == 1

    async def test_eventbrite_event_query_start_time_5(self) -> None:
        results = await self._setup_results(datetime(2024, 12, 18, 10, 10), timedelta(minutes=-15))
        assert len(results) == 0

    async def test_eventbrite_event_query_start_time_6(self) -> None:
        results = await self._setup_results(datetime(2024, 12, 18, 10, 10), timedelta(minutes=15))
        assert len(results) == 0

    async def test_eventbrite_event_query_start_time_7(self) -> None:
        results = await self._setup_results(datetime(2024, 12, 18, 10, 30), timedelta(minutes=-10))
        assert len(results) == 0

    async def test_eventbrite_event_query_start_time_7_5(self) -> None:
        results = await self._setup_results(datetime(2024, 12, 18, 10, 30), timedelta(minutes=5))
        assert len(results) == 1

    async def test_eventbrite_event_query_start_time_8(self) -> None:
        results = await self._setup_results(datetime(2024, 12, 18, 10, 50), timedelta(minutes=12))
        assert len(results) == 0

    async def test_eventbrite_event_query_start_time_9(self) -> None:
        results = await self._setup_results(datetime(2024, 12, 18, 10, 55), timedelta(minutes=10))
        assert len(results) == 0

    async def test_eventbrite_event_query_start_time_10(self) -> None:
        results = await self._setup_results(datetime(2024, 12, 18, 10, 55), timedelta(minutes=-10))
        assert len(results) == 1

    async def test_eventbrite_event_query_search_area(self) -> None:
        async with self.db_session.begin() as session:
            EventbriteEventOrm(
                session,
                eventbrite_event_id=self.anystr("eventbrite_event_id"),
                eventbrite_organizer_id=self.anystr("eventbrite_organizer_id"),
                title=self.anystr(),
                google_place_id=self.anystr(),
                vivial_activity_category_id=self.anyuuid(),
                vivial_activity_format_id=self.anyuuid(),
                start_time=self.anydatetime(past=True),
                end_time=self.anydatetime(future=True),
                timezone=self.anytimezone(),
                min_cost_cents=0,
                max_cost_cents=self.anyint(min=1000, max=9999),
                lat=self.anylatitude("lat"),
                lon=self.anylongitude("lon"),
            )

        async with self.db_session.begin() as session:
            search_area = GeoArea(
                center=GeoPoint(lat=self.getlatitude("lat"), lon=self.getlongitude("lon")), rad=Distance(miles=0.1)
            )
            results = (
                await session.scalars(
                    EventbriteEventOrm.select(
                        within_areas=[search_area],
                    )
                )
            ).all()

            assert len(results) == 1, "query failed, but expected 1 result"

            # Move the search area to the antipode
            antipodesign = 1 if self.getlongitude("lon") <= 0 else -1
            search_area = GeoArea(
                center=GeoPoint(lat=-self.getlatitude("lat"), lon=self.getlongitude("lon") + (180 * antipodesign)),
                rad=Distance(miles=0.1),
            )
            results = (
                await session.scalars(
                    EventbriteEventOrm.select(
                        within_areas=[search_area],
                    )
                )
            ).all()

            assert len(results) == 0, "query expected to fail, but found a result"

    async def test_eventbrite_event_update_existing_record(self) -> None:
        async with self.db_session.begin() as session:
            EventbriteEventOrm(
                session,
                eventbrite_event_id=self.anystr("eventbrite_event_id"),
                eventbrite_organizer_id=self.anystr("eventbrite_organizer_id"),
                title=self.anystr(),
                google_place_id=self.anystr(),
                vivial_activity_category_id=self.anyuuid(),
                vivial_activity_format_id=self.anyuuid(),
                start_time=self.anydatetime("start_time", past=True),
                end_time=self.anydatetime("end_time", future=True),
                timezone=self.anytimezone(),
                min_cost_cents=self.anyint("min_cost", min=0, max=999),
                max_cost_cents=self.anyint("max_cost", min=1000, max=9999),
                lat=self.anylatitude("lat"),
                lon=self.anylongitude("lon"),
            )

        async with self.db_session.begin() as session:
            qobj = (
                await session.scalars(
                    EventbriteEventOrm.select(
                        eventbrite_event_id=self.getstr("eventbrite_event_id"),
                    )
                )
            ).one()

            qobj.update(
                title=self.anystr("new title"),
                google_place_id=None,
                vivial_activity_category_id=self.anyuuid("new vivial_activity_category_id"),
                vivial_activity_format_id=self.anyuuid("new vivial_activity_format_id"),
                start_time=self.anydatetime("new start_time", past=True),
                end_time=self.anydatetime("new end_time", future=True),
                timezone=self.anytimezone("new timezone"),
                min_cost_cents=self.anyint("new min_cost", min=0, max=999),
                max_cost_cents=self.anyint("new max_cost", min=1000, max=9999),
                lat=self.anylatitude("new lat"),
                lon=self.anylongitude("new lon"),
            )

        async with self.db_session.begin() as session:
            qobj = (
                await session.scalars(
                    EventbriteEventOrm.select(
                        eventbrite_event_id=self.getstr("eventbrite_event_id"),
                    )
                )
            ).one()

            assert qobj.eventbrite_event_id == self.getstr("eventbrite_event_id")
            assert qobj.title == self.getdatetime("new title")
            assert qobj.vivial_activity_category_id == self.getdatetime("new vivial_activity_category_id")
            assert qobj.vivial_activity_format_id == self.getdatetime("new vivial_activity_format_id")
            assert qobj.start_time_utc == self.getdatetime("new start_time")
            assert qobj.end_time_utc == self.getdatetime("new end_time")
            assert qobj.max_cost_cents == self.getint("new max_cost")
            assert qobj.min_cost_cents == self.getint("new min_cost")
            assert qobj.timezone == self.gettimezone("new timezone")
            assert qobj.coordinates_to_geopoint().lat == self.getlatitude("new lat")
            assert qobj.coordinates_to_geopoint().lon == self.getlatitude("new lon")

    async def _setup_eventbrite_events_for_query_by_activity_category(
        self, activity_category_id: UUID
    ) -> EventbriteEventOrm:
        async with self.db_session.begin() as session:
            obj = EventbriteEventOrm(
                session,
                eventbrite_event_id=self.anystr(),
                eventbrite_organizer_id=self.anystr(),
                title=self.anystr(),
                google_place_id=None,
                vivial_activity_category_id=activity_category_id,
                vivial_activity_format_id=self.anyuuid(),
                start_time=self.anydatetime(past=True),
                end_time=self.anydatetime(future=True),
                timezone=self.anytimezone(),
                min_cost_cents=self.anyint(min=0, max=999),
                max_cost_cents=self.anyint(min=1000, max=9999),
                lat=self.anylatitude(),
                lon=self.anylongitude(),
            )

        return obj

    async def test_eventbrite_event_query_vivial_activity_category_ids_1(self) -> None:
        activity_category_id = random.choice(ActivityCategoryOrm.all()).id
        obj = await self._setup_eventbrite_events_for_query_by_activity_category(activity_category_id)

        async with self.db_session.begin() as session:
            result = (
                await session.scalars(EventbriteEventOrm.select(vivial_activity_category_ids=[activity_category_id]))
            ).all()
            assert len(result) == 1
            assert result[0].id == obj.id

    async def test_eventbrite_event_query_vivial_activity_category_ids_2(self) -> None:
        activity_category_id_1 = random.choice(ActivityCategoryOrm.all()).id
        activity_category_id_2 = random.choice(ActivityCategoryOrm.all()).id

        await self._setup_eventbrite_events_for_query_by_activity_category(activity_category_id_1)
        obj_2 = await self._setup_eventbrite_events_for_query_by_activity_category(activity_category_id_2)

        async with self.db_session.begin() as session:
            result = (
                await session.scalars(EventbriteEventOrm.select(vivial_activity_category_ids=[activity_category_id_2]))
            ).all()
            assert len(result) == 1
            assert result[0].id == obj_2.id

    async def test_eventbrite_event_query_vivial_activity_category_ids_3(self) -> None:
        activity_category_id_1 = random.choice(ActivityCategoryOrm.all()).id
        activity_category_id_2 = random.choice(ActivityCategoryOrm.all()).id

        await self._setup_eventbrite_events_for_query_by_activity_category(activity_category_id_1)
        await self._setup_eventbrite_events_for_query_by_activity_category(activity_category_id_1)
        obj_2 = await self._setup_eventbrite_events_for_query_by_activity_category(activity_category_id_2)
        obj_3 = await self._setup_eventbrite_events_for_query_by_activity_category(activity_category_id_2)

        async with self.db_session.begin() as session:
            result = (
                await session.scalars(EventbriteEventOrm.select(vivial_activity_category_ids=[activity_category_id_2]))
            ).all()
            assert len(result) == 2
            assert result[0].id == obj_2.id
            assert result[1].id == obj_3.id

    async def test_eventbrite_event_query_vivial_activity_category_ids_4(self) -> None:
        activity_category_id_1 = random.choice(ActivityCategoryOrm.all()).id
        activity_category_id_2 = random.choice(ActivityCategoryOrm.all()).id

        obj_1 = await self._setup_eventbrite_events_for_query_by_activity_category(activity_category_id_1)
        obj_2 = await self._setup_eventbrite_events_for_query_by_activity_category(activity_category_id_1)
        obj_3 = await self._setup_eventbrite_events_for_query_by_activity_category(activity_category_id_2)
        obj_4 = await self._setup_eventbrite_events_for_query_by_activity_category(activity_category_id_2)

        async with self.db_session.begin() as session:
            result = (
                await session.scalars(
                    EventbriteEventOrm.select(
                        vivial_activity_category_ids=[activity_category_id_1, activity_category_id_2]
                    )
                )
            ).all()
            assert len(result) == 4
            assert result[0].id == obj_1.id
            assert result[1].id == obj_2.id
            assert result[2].id == obj_3.id
            assert result[3].id == obj_4.id

    async def test_eventbrite_event_query_vivial_activity_category_ids_5(self) -> None:
        activity_category_id_1 = random.choice(ActivityCategoryOrm.all()).id
        activity_category_id_2 = random.choice(ActivityCategoryOrm.all()).id

        obj_1 = await self._setup_eventbrite_events_for_query_by_activity_category(activity_category_id_1)

        async with self.db_session.begin() as session:
            result = (
                await session.scalars(
                    EventbriteEventOrm.select(
                        vivial_activity_category_ids=[activity_category_id_1, activity_category_id_2]
                    )
                )
            ).all()
            assert len(result) == 1
            assert result[0].id == obj_1.id

    async def test_eventbrite_event_query_vivial_activity_category_ids_6(self) -> None:
        activity_category_id_1 = random.choice(ActivityCategoryOrm.all()).id
        activity_category_id_2 = random.choice(ActivityCategoryOrm.all()).id

        await self._setup_eventbrite_events_for_query_by_activity_category(activity_category_id_1)

        async with self.db_session.begin() as session:
            result = (
                await session.scalars(EventbriteEventOrm.select(vivial_activity_category_ids=[activity_category_id_2]))
            ).all()
            assert len(result) == 0
