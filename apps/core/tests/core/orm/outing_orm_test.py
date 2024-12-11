import random
from eave.core.lib.geo import GeoPoint
from eave.core.orm.account import AccountOrm
from eave.core.orm.activity import ActivityOrm
from eave.core.orm.image import ImageOrm
from eave.core.orm.outing import OutingActivityOrm, OutingOrm, OutingReservationOrm
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.shared.address import Address
from eave.core.shared.enums import ActivitySource, OutingBudget, RestaurantSource

from ..base import BaseTestCase


class TestOutingOrms(BaseTestCase):
    async def test_outing_associations(self) -> None:
        async with self.db_session.begin() as session:
            account = AccountOrm(
                email=self.anyemail(),
                plaintext_password=self.anystr(),
            )
            session.add(account)

            survey = SurveyOrm(
                account=account,
                budget=OutingBudget.INEXPENSIVE,
                headcount=self.anyint(min=1,max=2),
                search_area_ids=[s.id for s in random.choices(SearchRegionOrm.all(), k=3)],
                start_time_utc=self.anydatetime(future=True),
                timezone=self.anytimezone(),
                visitor_id=self.anyuuid("visitor id"),
            )
            session.add(survey)

            outing = OutingOrm(
                account=account,
                survey=survey,
                visitor_id=survey.visitor_id,
            )
            session.add(outing)

            activity = OutingActivityOrm(
                outing=outing,
                headcount=survey.headcount,
                source=ActivitySource.EVENTBRITE,
                source_id=self.anydigits(),
                start_time_utc=self.anydatetime(future=True),
                timezone=survey.timezone,
            )
            outing.activities.append(activity)

            reservation = OutingReservationOrm(
                outing=outing,
                headcount=survey.headcount,
                source=RestaurantSource.GOOGLE_PLACES,
                source_id=self.anystr(),
                start_time_utc=self.anydatetime(future=True),
                timezone=survey.timezone,
            )
            outing.reservations.append(reservation)

        async with self.db_session.begin() as session:
            outing_fetched = await OutingOrm.get_one(session, outing.id)

            assert outing_fetched.id == outing.id

            assert outing_fetched.survey.id == survey.id
            assert outing_fetched.survey_id == survey.id

            assert outing_fetched.account is not None
            assert outing_fetched.account.id == account.id
            assert outing_fetched.account_id == account.id

            assert len(outing_fetched.activities) == 1
            assert outing_fetched.activities[0].outing_id == outing.id
            assert outing_fetched.activities[0].outing.id == outing.id

            assert len(outing_fetched.reservations) == 1
            assert outing_fetched.reservations[0].outing_id == outing.id
            assert outing_fetched.reservations[0].outing.id == outing.id

    async def test_outing_without_account(self) -> None:
        async with self.db_session.begin() as session:
            survey = SurveyOrm(
                account=None,
                budget=OutingBudget.INEXPENSIVE,
                headcount=self.anyint(min=1,max=2),
                search_area_ids=[s.id for s in random.choices(SearchRegionOrm.all(), k=3)],
                start_time_utc=self.anydatetime(future=True),
                timezone=self.anytimezone(),
                visitor_id=self.anyuuid("visitor id"),
            )
            session.add(survey)

            outing = OutingOrm(
                account=None,
                survey=survey,
                visitor_id=survey.visitor_id,
            )
            session.add(outing)

        async with self.db_session.begin() as session:
            outing_fetched = await OutingOrm.get_one(session, outing.id)

            assert outing_fetched.id == outing.id
            assert outing_fetched.account is None

    async def test_outing_activity_initialization(self) -> None:
        async with self.db_session.begin() as session:
            survey = SurveyOrm(
                account=None,
                budget=OutingBudget.INEXPENSIVE,
                headcount=self.anyint(min=1,max=2),
                search_area_ids=[s.id for s in random.choices(SearchRegionOrm.all(), k=3)],
                start_time_utc=self.anydatetime(future=True),
                timezone=self.anytimezone(),
                visitor_id=self.anyuuid("visitor id"),
            )
            session.add(survey)

            outing = OutingOrm(
                account=None,
                survey=survey,
                visitor_id=survey.visitor_id,
            )
            session.add(outing)

            outing_activity_new = OutingActivityOrm(
                outing=outing,
                headcount=survey.headcount,
                source=ActivitySource.EVENTBRITE,
                source_id=self.anydigits("source_id"),
                start_time_utc=self.anydatetime("start_time_utc", future=True),
                timezone=survey.timezone,
            )
            session.add(outing_activity_new)

        async with self.db_session.begin() as session:
            outing_activity_fetched = await session.get_one(OutingActivityOrm, (outing.id, self.getdigits("source_id")))

            assert outing_activity_fetched.id == outing_activity_new.id
            assert outing_activity_fetched.outing.id == outing.id
            assert outing_activity_fetched.outing_id == outing.id
            assert outing_activity_fetched.source_id == self.getstr("source_id")
            assert outing_activity_fetched.source == ActivitySource.EVENTBRITE
            assert outing_activity_fetched.start_time_utc == self.getdatetime("start_time_utc")
            assert outing_activity_fetched.start_time_local == self.getdatetime("start_time_utc").astimezone(survey.timezone)
            assert outing_activity_fetched.timezone == survey.timezone
            assert outing_activity_fetched.headcount == survey.headcount

    async def test_outing_reservation_initialization(self) -> None:
        async with self.db_session.begin() as session:
            survey = SurveyOrm(
                account=None,
                budget=OutingBudget.INEXPENSIVE,
                headcount=self.anyint(min=1,max=2),
                search_area_ids=[s.id for s in random.choices(SearchRegionOrm.all(), k=3)],
                start_time_utc=self.anydatetime(future=True),
                timezone=self.anytimezone(),
                visitor_id=self.anyuuid("visitor id"),
            )
            session.add(survey)

            outing = OutingOrm(
                account=None,
                survey=survey,
                visitor_id=survey.visitor_id,
            )
            session.add(outing)

            outing_reservation_new = OutingReservationOrm(
                outing=outing,
                headcount=survey.headcount,
                source=RestaurantSource.GOOGLE_PLACES,
                source_id=self.anydigits("source_id"),
                start_time_utc=self.anydatetime("start_time_utc", future=True),
                timezone=survey.timezone,
            )
            session.add(outing_reservation_new)

        async with self.db_session.begin() as session:
            outing_reservation_fetched = await session.get_one(OutingReservationOrm, (outing.id, self.getdigits("source_id")))

            assert outing_reservation_fetched.id == outing_reservation_new.id
            assert outing_reservation_fetched.outing.id == outing.id
            assert outing_reservation_fetched.outing_id == outing.id
            assert outing_reservation_fetched.source_id == self.getstr("source_id")
            assert outing_reservation_fetched.source == RestaurantSource.GOOGLE_PLACES
            assert outing_reservation_fetched.start_time_utc == self.getdatetime("start_time_utc")
            assert outing_reservation_fetched.start_time_local == self.getdatetime("start_time_utc").astimezone(survey.timezone)
            assert outing_reservation_fetched.timezone == survey.timezone
            assert outing_reservation_fetched.headcount == survey.headcount
