from datetime import timedelta

from eave.core.internal.orm.eventbrite_event import EventbriteEventOrm
from eave.core.outing.models.geo_area import GeoArea
from ..base import BaseTestCase


class TestEventbriteEventOrm(BaseTestCase):
    async def test_new_record(self) -> None:
        async with self.db_session.begin() as session:
            obj = EventbriteEventOrm(eventbrite_event_id=self.anystr("eventbrite_event_id"))
            obj.update(
                title=self.anystr(),
                subcategory_id=self.anyuuid(),
                format_id=self.anyuuid(),
                start_time=self.anydatetime("start_time", past=True),
                end_time=self.anydatetime("end_time", future=True),
                min_cost_cents=self.anyint("min_cost", min=0, max=999),
                max_cost_cents=self.anyint("max_cost", min=1000, max=9999),
                lat=self.anylatitude("lat"),
                lon=self.anylongitude("lon"),
            )

            session.add(obj)

        async with self.db_session.begin() as session:
            obj = (await EventbriteEventOrm.query(
                session,
                params=EventbriteEventOrm.QueryParams(eventbrite_event_id=self.getstr("eventbrite_event_id"))
            )).one()

            assert obj.eventbrite_event_id == self.getstr("eventbrite_event_id")
            assert obj.time_range.lower == self.getdatetime("start_time")
            assert obj.time_range.upper == self.getdatetime("end_time")
            assert obj.cost_cents_range.lower == self.getint("min_cost")
            assert obj.cost_cents_range.upper == self.getint("max_cost") + 1

    async def test_query_cost_range(self) -> None:
        async with self.db_session.begin() as session:
            obj = EventbriteEventOrm(eventbrite_event_id=self.anystr("eventbrite_event_id"))
            obj.update(
                title=self.anystr(),
                subcategory_id=self.anyuuid(),
                format_id=self.anyuuid(),
                start_time=self.anydatetime("start_time", past=True),
                end_time=self.anydatetime("end_time", future=True),
                min_cost_cents=self.anyint("min_cost", min=0, max=999),
                max_cost_cents=self.anyint("max_cost", min=2000, max=9999),
                lat=self.anylatitude("lat"),
                lon=self.anylongitude("lon"),
            )

            session.add(obj)

        async with self.db_session.begin() as session:
            results = (await EventbriteEventOrm.query(
                session,
                params=EventbriteEventOrm.QueryParams(
                    cost_range_contains=self.getint("min_cost") - 1, # out of range
                ),
            )).all()

            assert len(results) == 0, "query expected to fail, but found a result"

            results = (await EventbriteEventOrm.query(
                session,
                params=EventbriteEventOrm.QueryParams(
                    cost_range_contains=self.getint("max_cost") + 1, # out of range
                ),
            )).all()

            assert len(results) == 0, "query expected to fail, but found a result"

            results = (await EventbriteEventOrm.query(
                session,
                params=EventbriteEventOrm.QueryParams(
                    cost_range_contains=self.getint("min_cost"), # lower bound of range
                ),
            )).all()

            assert len(results) == 1, "query failed, but a result was expected"

            results = (await EventbriteEventOrm.query(
                session,
                params=EventbriteEventOrm.QueryParams(
                    cost_range_contains=self.getint("max_cost"), # upper bound of range
                ),
            )).all()

            assert len(results) == 1, "query failed, but a result was expected"

    async def test_query_time_range(self) -> None:
        async with self.db_session.begin() as session:
            obj = EventbriteEventOrm(eventbrite_event_id=self.anystr("eventbrite_event_id"))
            obj.update(
                title=self.anystr(),
                subcategory_id=self.anyuuid(),
                format_id=self.anyuuid(),
                start_time=self.anydatetime("start_time", offset=-60*60*24),
                end_time=self.anydatetime("end_time", offset=60*60*24),
                min_cost_cents=self.anyint("min_cost", min=0, max=999),
                max_cost_cents=self.anyint("max_cost", min=2000, max=9999),
                lat=self.anylatitude("lat"),
                lon=self.anylongitude("lon"),
            )

            session.add(obj)

        async with self.db_session.begin() as session:
            results = (await EventbriteEventOrm.query(
                session,
                params=EventbriteEventOrm.QueryParams(
                    time_range_contains=self.getdatetime("start_time") - timedelta(minutes=1), # out of range
                ),
            )).all()

            assert len(results) == 0, "query expected to fail, but found a result"

            results = (await EventbriteEventOrm.query(
                session,
                params=EventbriteEventOrm.QueryParams(
                    time_range_contains=self.getdatetime("end_time") + timedelta(minutes=1), # out of range
                ),
            )).all()

            assert len(results) == 0, "query expected to fail, but found a result"

            results = (await EventbriteEventOrm.query(
                session,
                params=EventbriteEventOrm.QueryParams(
                    time_range_contains=self.getdatetime("start_time"), # lower bound
                ),
            )).all()

            assert len(results) == 1, "query failed, but expected 1 result"

            results = (await EventbriteEventOrm.query(
                session,
                params=EventbriteEventOrm.QueryParams(
                    time_range_contains=self.getdatetime("start_time") + timedelta(minutes=1), # just inside of the lower bound
                ),
            )).all()

            assert len(results) == 1, "query failed, but expected 1 result"

            results = (await EventbriteEventOrm.query(
                session,
                params=EventbriteEventOrm.QueryParams(
                    time_range_contains=self.getdatetime("end_time"), # upper bound EXCLUSIVE
                ),
            )).all()

            assert len(results) == 0, "query expected to fail, but found a result"

            results = (await EventbriteEventOrm.query(
                session,
                params=EventbriteEventOrm.QueryParams(
                    time_range_contains=self.getdatetime("end_time") - timedelta(minutes=1), # just inside of the upper bound
                ),
            )).all()

            assert len(results) == 1, "query failed, but expected 1 result"

    async def test_query_search_area(self) -> None:
        async with self.db_session.begin() as session:
            obj = EventbriteEventOrm(eventbrite_event_id=self.anystr("eventbrite_event_id"))
            obj.update(
                title=self.anystr(),
                subcategory_id=self.anyuuid(),
                format_id=self.anyuuid(),
                start_time=self.anydatetime(),
                end_time=self.anydatetime(),
                min_cost_cents=self.anyint(),
                max_cost_cents=self.anyint(),
                lat=self.anylatitude("lat"),
                lon=self.anylongitude("lon"),
            )

            session.add(obj)

        async with self.db_session.begin() as session:
            search_area = GeoArea(lat=self.getlatitude("lat"), lon=self.getlongitude("lon"), rad_miles=0.1)
            results = (await EventbriteEventOrm.query(
                session,
                params=EventbriteEventOrm.QueryParams(
                    within_area=search_area,
                ),
            )).all()

            assert len(results) == 1, "query failed, but expected 1 result"

            # Move the search area to the antipode
            antipodesign = 1 if self.getlongitude("lon") <= 0 else -1
            search_area = GeoArea(lat=-self.getlatitude("lat"), lon=self.getlongitude("lon")+(180*antipodesign), rad_miles=0.1)
            results = (await EventbriteEventOrm.query(
                session,
                params=EventbriteEventOrm.QueryParams(
                    within_area=search_area,
                ),
            )).all()

            assert len(results) == 0, "query expected to fail, but found a result"


    async def test_update_existing_record(self) -> None:
        async with self.db_session.begin() as session:
            obj = EventbriteEventOrm(eventbrite_event_id=self.anystr("eventbrite_event_id"))
            obj.update(
                title=self.anystr(),
                subcategory_id=self.anyuuid(),
                format_id=self.anyuuid(),
                start_time=self.anydatetime("start_time", past=True),
                end_time=self.anydatetime("end_time", future=True),
                min_cost_cents=self.anyint("min_cost", min=0, max=999),
                max_cost_cents=self.anyint("max_cost", min=1000, max=9999),
                lat=self.anylatitude("lat"),
                lon=self.anylongitude("lon"),
            )

            session.add(obj)

        async with self.db_session.begin() as session:
            qobj = (await EventbriteEventOrm.query(
                session,
                params=EventbriteEventOrm.QueryParams(eventbrite_event_id=self.getstr("eventbrite_event_id"))
            )).one()

            qobj.update(
                title=self.anystr("new title"),
                subcategory_id=self.anyuuid("new subcategory_id"),
                format_id=self.anyuuid("new format_id"),
                start_time=self.anydatetime("new start_time", past=True),
                end_time=self.anydatetime("new end_time", future=True),
                min_cost_cents=self.anyint("new min_cost", min=0, max=999),
                max_cost_cents=self.anyint("new max_cost", min=1000, max=9999),
                lat=self.anylatitude("new lat"),
                lon=self.anylongitude("new lon"),
            )

        async with self.db_session.begin() as session:
            qobj = (await EventbriteEventOrm.query(
                session,
                params=EventbriteEventOrm.QueryParams(eventbrite_event_id=self.getstr("eventbrite_event_id"))
            )).one()

            assert qobj.eventbrite_event_id == self.getstr("eventbrite_event_id")
            assert qobj.title == self.getdatetime("new title")
            assert qobj.subcategory_id == self.getdatetime("new subcategory_id")
            assert qobj.format_id == self.getdatetime("new format_id")
            assert qobj.time_range.upper == self.getdatetime("new end_time")
            assert qobj.cost_cents_range.lower == self.getint("new min_cost")
            assert qobj.cost_cents_range.upper == self.getint("new max_cost") + 1
