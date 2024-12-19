from datetime import datetime, timedelta
import random
from typing import Sequence
from uuid import UUID

from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.eventbrite_event import EventbriteEventOrm
from eave.core.shared.geo import Distance, GeoArea, GeoPoint
from eave.stdlib.time import ONE_DAY_IN_SECONDS

from ..base import BaseTestCase


class TestEventbriteEventOrm(BaseTestCase):
    async def test_eventbrite_event_new_event_record(self) -> None:
        async with self.db_session.begin() as session:
            obj = EventbriteEventOrm(
                session,
                eventbrite_event_id=self.anystr("eventbrite_event_id"),
                eventbrite_organizer_id=self.anystr("eventbrite_organizer_id"),
                title=self.anystr(),
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

    async def test_eventbrite_event_query_max_cost(self) -> None:
        async with self.db_session.begin() as session:
            obj = EventbriteEventOrm(
                session,
                eventbrite_event_id=self.anystr("eventbrite_event_id"),
                eventbrite_organizer_id=self.anystr("eventbrite_organizer_id"),
                title=self.anystr(),
                vivial_activity_category_id=self.anyuuid(),
                vivial_activity_format_id=self.anyuuid(),
                start_time=self.anydatetime("start_time", past=True),
                end_time=self.anydatetime("end_time", future=True),
                timezone=self.anytimezone(),
                min_cost_cents=self.anyint("min_cost", min=0, max=1999),
                max_cost_cents=self.anyint("max_cost", min=2000, max=9999),
                lat=self.anylatitude("lat"),
                lon=self.anylongitude("lon"),
            )

        async with self.db_session.begin() as session:
            results = (
                await session.scalars(
                    EventbriteEventOrm.select(
                        up_to_cost_cents=self.getint("max_cost"),  # the event's max_cost is equal to the query limit
                    )
                )
            ).all()

            assert len(results) == 1, "query expected to find a result, but found none"

            results = (
                await session.scalars(
                    EventbriteEventOrm.select(
                        up_to_cost_cents=self.getint("max_cost")
                        - 1,  # the event's max_cost is 1 higher than the query limit
                    )
                )
            ).all()

            assert len(results) == 0, "query expected to fail, but found a result"

            results = (
                await session.scalars(
                    EventbriteEventOrm.select(
                        up_to_cost_cents=self.getint("max_cost")
                        + 1,  # the event's max_cost is 1 lower than the query limit
                    )
                )
            ).all()

            assert len(results) == 1, "query failed, but a result was expected"

            results = (
                await session.scalars(
                    EventbriteEventOrm.select(
                        up_to_cost_cents=0,
                    )
                )
            ).all()

            assert len(results) == 0, "query expected to fail, but found a result"

        async with self.db_session.begin() as session:
            obj = await EventbriteEventOrm.get_one(session, obj.id)
            obj.max_cost_cents = 0

        async with self.db_session.begin() as session:
            results = (
                await session.scalars(
                    EventbriteEventOrm.select(
                        up_to_cost_cents=self.anyint(min=100),
                    )
                )
            ).all()

            assert len(results) == 1, "query expected to find a result, but found none"

            results = (
                await session.scalars(
                    EventbriteEventOrm.select(
                        up_to_cost_cents=0,
                    )
                )
            ).all()

            assert len(results) == 1, "query expected to find a result, but found none"

    async def _setup_results(self, start_time: datetime, delta: timedelta) -> Sequence[EventbriteEventOrm]:
        async with self.db_session.begin() as session:
            EventbriteEventOrm(
                session,
                eventbrite_event_id=self.anystr(),
                eventbrite_organizer_id=self.anystr(),
                title=self.anystr(),
                vivial_activity_category_id=self.anyuuid(),
                vivial_activity_format_id=self.anyuuid(),
                start_time=start_time,
                end_time=self.anydatetime(offset=ONE_DAY_IN_SECONDS),
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
        results = await self._setup_results(self.anydatetime("start_time", offset=ONE_DAY_IN_SECONDS), timedelta(minutes=-120),
        )
        assert len(results) == 0

    async def test_eventbrite_event_query_start_time_21(self) -> None:
        results = await self._setup_results(self.anydatetime("start_time", offset=ONE_DAY_IN_SECONDS), timedelta(minutes=120))
        assert len(results) == 0

    async def test_eventbrite_event_query_start_time_22(self) -> None:
        results = await self._setup_results(self.anydatetime("start_time", offset=ONE_DAY_IN_SECONDS), timedelta(minutes=15))
        assert len(results) == 0

    async def test_eventbrite_event_query_start_time_23(self) -> None:
        results = await self._setup_results(self.anydatetime("start_time", offset=ONE_DAY_IN_SECONDS), timedelta(minutes=-16))
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
            obj = EventbriteEventOrm(
                session,
                eventbrite_event_id=self.anystr("eventbrite_event_id"),
                eventbrite_organizer_id=self.anystr("eventbrite_organizer_id"),
                title=self.anystr(),
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

    async def _setup_eventbrite_events_for_query_by_activity_category(self, activity_category_id: UUID) -> EventbriteEventOrm:
        async with self.db_session.begin() as session:
            obj = EventbriteEventOrm(
                session,
                eventbrite_event_id=self.anystr(),
                eventbrite_organizer_id=self.anystr(),
                title=self.anystr(),
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
            result = (await session.scalars(EventbriteEventOrm.select(vivial_activity_category_ids=[activity_category_id]))).all()
            assert len(result) == 1
            assert result[0].id == obj.id

    async def test_eventbrite_event_query_vivial_activity_category_ids_2(self) -> None:
        activity_category_id_1 = random.choice(ActivityCategoryOrm.all()).id
        activity_category_id_2 = random.choice(ActivityCategoryOrm.all()).id

        await self._setup_eventbrite_events_for_query_by_activity_category(activity_category_id_1)
        obj_2 = await self._setup_eventbrite_events_for_query_by_activity_category(activity_category_id_2)

        async with self.db_session.begin() as session:
            result = (await session.scalars(EventbriteEventOrm.select(vivial_activity_category_ids=[activity_category_id_2]))).all()
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
            result = (await session.scalars(EventbriteEventOrm.select(vivial_activity_category_ids=[activity_category_id_2]))).all()
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
            result = (await session.scalars(EventbriteEventOrm.select(vivial_activity_category_ids=[activity_category_id_1, activity_category_id_2]))).all()
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
            result = (await session.scalars(EventbriteEventOrm.select(vivial_activity_category_ids=[activity_category_id_1, activity_category_id_2]))).all()
            assert len(result) == 1
            assert result[0].id == obj_1.id

    async def test_eventbrite_event_query_vivial_activity_category_ids_6(self) -> None:
        activity_category_id_1 = random.choice(ActivityCategoryOrm.all()).id
        activity_category_id_2 = random.choice(ActivityCategoryOrm.all()).id

        await self._setup_eventbrite_events_for_query_by_activity_category(activity_category_id_1)

        async with self.db_session.begin() as session:
            result = (await session.scalars(EventbriteEventOrm.select(vivial_activity_category_ids=[activity_category_id_2]))).all()
            assert len(result) == 0
