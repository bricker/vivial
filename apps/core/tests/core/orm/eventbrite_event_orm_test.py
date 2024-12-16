from datetime import timedelta

from eave.core.orm.eventbrite_event import EventbriteEventOrm
from eave.core.shared.geo import Distance, GeoArea, GeoPoint
from eave.stdlib.time import ONE_DAY_IN_SECONDS

from ..base import BaseTestCase


class TestEventbriteEventOrm(BaseTestCase):
    async def test_new_event_record(self) -> None:
        async with self.db_session.begin() as session:
            obj = EventbriteEventOrm(
                session,
                eventbrite_event_id=self.anystr("eventbrite_event_id"),
                eventbrite_organizer_id=self.anystr("eventbrite_organizer_id"),
            )
            obj.update(
                title=self.anystr(),
                vivial_activity_category_id=self.anyuuid(),
                vivial_activity_format_id=self.anyuuid(),
                start_time=self.anydatetime("start_time", past=True),
                end_time=self.anydatetime("end_time", future=True),
                timezone=self.anytimezone("timezone"),
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
            assert obj.time_range_utc.lower == self.getdatetime("start_time")
            assert obj.time_range_utc.upper == self.getdatetime("end_time")
            assert obj.max_cost_cents == self.getint("max_cost")
            assert obj.timezone == self.gettimezone("timezone")

    async def test_query_max_cost(self) -> None:
        async with self.db_session.begin() as session:
            obj = EventbriteEventOrm(
                session,
                eventbrite_event_id=self.anystr("eventbrite_event_id"),
                eventbrite_organizer_id=self.anystr("eventbrite_organizer_id"),
            )
            obj.update(
                title=self.anystr(),
                vivial_activity_category_id=self.anyuuid(),
                vivial_activity_format_id=self.anyuuid(),
                start_time=self.anydatetime("start_time", past=True),
                end_time=self.anydatetime("end_time", future=True),
                timezone=self.anytimezone(),
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

    async def test_query_time_range(self) -> None:
        async with self.db_session.begin() as session:
            obj = EventbriteEventOrm(
                session,
                eventbrite_event_id=self.anystr("eventbrite_event_id"),
                eventbrite_organizer_id=self.anystr("eventbrite_organizer_id"),
            )
            obj.update(
                title=self.anystr(),
                vivial_activity_category_id=self.anyuuid(),
                vivial_activity_format_id=self.anyuuid(),
                start_time=self.anydatetime("start_time", offset=-ONE_DAY_IN_SECONDS),
                end_time=self.anydatetime("end_time", offset=ONE_DAY_IN_SECONDS),
                timezone=self.anytimezone(),
                max_cost_cents=self.anyint("max_cost", min=2000, max=9999),
                lat=self.anylatitude("lat"),
                lon=self.anylongitude("lon"),
            )

        async with self.db_session.begin() as session:
            results = (
                await session.scalars(
                    EventbriteEventOrm.select(
                        time_range_contains=self.getdatetime("start_time") - timedelta(minutes=1),  # out of range
                    )
                )
            ).all()

            assert len(results) == 0, "query expected to fail, but found a result"

            results = (
                await session.scalars(
                    EventbriteEventOrm.select(
                        time_range_contains=self.getdatetime("end_time") + timedelta(minutes=1),  # out of range
                    )
                )
            ).all()

            assert len(results) == 0, "query expected to fail, but found a result"

            results = (
                await session.scalars(
                    EventbriteEventOrm.select(
                        time_range_contains=self.getdatetime("start_time"),  # lower bound
                    )
                )
            ).all()

            assert len(results) == 1, "query failed, but expected 1 result"

            results = (
                await session.scalars(
                    EventbriteEventOrm.select(
                        time_range_contains=self.getdatetime("start_time")
                        + timedelta(minutes=1),  # just inside of the lower bound
                    )
                )
            ).all()

            assert len(results) == 1, "query failed, but expected 1 result"

            results = (
                await session.scalars(
                    EventbriteEventOrm.select(
                        time_range_contains=self.getdatetime("end_time"),  # upper bound EXCLUSIVE
                    )
                )
            ).all()

            assert len(results) == 0, "query expected to fail, but found a result"

            results = (
                await session.scalars(
                    EventbriteEventOrm.select(
                        time_range_contains=self.getdatetime("end_time")
                        - timedelta(minutes=1),  # just inside of the upper bound
                    )
                )
            ).all()

            assert len(results) == 1, "query failed, but expected 1 result"

    async def test_query_search_area(self) -> None:
        async with self.db_session.begin() as session:
            obj = EventbriteEventOrm(
                session,
                eventbrite_event_id=self.anystr("eventbrite_event_id"),
                eventbrite_organizer_id=self.anystr("eventbrite_organizer_id"),
            )
            obj.update(
                title=self.anystr(),
                vivial_activity_category_id=self.anyuuid(),
                vivial_activity_format_id=self.anyuuid(),
                start_time=self.anydatetime(past=True),
                end_time=self.anydatetime(future=True),
                timezone=self.anytimezone(),
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

    async def test_update_existing_record(self) -> None:
        async with self.db_session.begin() as session:
            obj = EventbriteEventOrm(
                session,
                eventbrite_event_id=self.anystr("eventbrite_event_id"),
                eventbrite_organizer_id=self.anystr("eventbrite_organizer_id"),
            )
            obj.update(
                title=self.anystr(),
                vivial_activity_category_id=self.anyuuid(),
                vivial_activity_format_id=self.anyuuid(),
                start_time=self.anydatetime("start_time", past=True),
                end_time=self.anydatetime("end_time", future=True),
                timezone=self.anytimezone(),
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
                timezone=self.anytimezone(),
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
            assert qobj.time_range_utc.upper == self.getdatetime("new end_time")
            assert qobj.max_cost_cents == self.getint("new max_cost")
