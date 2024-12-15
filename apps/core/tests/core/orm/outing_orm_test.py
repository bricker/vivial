from eave.core.orm.outing import OutingActivityOrm, OutingOrm, OutingReservationOrm
from eave.core.shared.enums import ActivitySource, RestaurantSource

from ..base import BaseTestCase


class TestOutingOrms(BaseTestCase):
    async def test_outing_associations(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            survey = self.make_survey(session, None)

            outing = OutingOrm(
                session,
                account=account,
                survey=survey,
                visitor_id=survey.visitor_id,
            )

            activity = OutingActivityOrm(
                session,
                outing=outing,
                headcount=survey.headcount,
                source=ActivitySource.EVENTBRITE,
                source_id=self.anydigits(),
                start_time_utc=self.anydatetime(future=True),
                timezone=survey.timezone,
            )
            outing.activities.append(activity)

            reservation = OutingReservationOrm(
                session,
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
            survey = self.make_survey(session, None)

            outing = OutingOrm(
                session,
                account=None,
                survey=survey,
                visitor_id=survey.visitor_id,
            )

        async with self.db_session.begin() as session:
            outing_fetched = await OutingOrm.get_one(session, outing.id)

            assert outing_fetched.id == outing.id
            assert outing_fetched.account is None

    async def test_outing_activity_initialization(self) -> None:
        async with self.db_session.begin() as session:
            survey = self.make_survey(session, None)

            outing = OutingOrm(
                session,
                account=None,
                survey=survey,
                visitor_id=survey.visitor_id,
            )

            outing_activity_new = OutingActivityOrm(
                session,
                outing=outing,
                headcount=survey.headcount,
                source=ActivitySource.EVENTBRITE,
                source_id=self.anydigits("source_id"),
                start_time_utc=self.anydatetime("start_time_utc", future=True),
                timezone=survey.timezone,
            )

        async with self.db_session.begin() as session:
            outing_activity_fetched = await session.get_one(OutingActivityOrm, (outing.id, self.getdigits("source_id")))

            assert outing_activity_fetched.id == outing_activity_new.id
            assert outing_activity_fetched.outing.id == outing.id
            assert outing_activity_fetched.outing_id == outing.id
            assert outing_activity_fetched.source_id == self.getstr("source_id")
            assert outing_activity_fetched.source == ActivitySource.EVENTBRITE
            assert outing_activity_fetched.start_time_utc == self.getdatetime("start_time_utc")
            assert outing_activity_fetched.start_time_local == self.getdatetime("start_time_utc").astimezone(
                survey.timezone
            )
            assert outing_activity_fetched.timezone == survey.timezone
            assert outing_activity_fetched.headcount == survey.headcount

    async def test_outing_reservation_initialization(self) -> None:
        async with self.db_session.begin() as session:
            survey = self.make_survey(session, None)

            outing = OutingOrm(
                session,
                account=None,
                survey=survey,
                visitor_id=survey.visitor_id,
            )

            outing_reservation_new = OutingReservationOrm(
                session,
                outing=outing,
                headcount=survey.headcount,
                source=RestaurantSource.GOOGLE_PLACES,
                source_id=self.anydigits("source_id"),
                start_time_utc=self.anydatetime("start_time_utc", future=True),
                timezone=survey.timezone,
            )

        async with self.db_session.begin() as session:
            outing_reservation_fetched = await session.get_one(
                OutingReservationOrm, (outing.id, self.getdigits("source_id"))
            )

            assert outing_reservation_fetched.id == outing_reservation_new.id
            assert outing_reservation_fetched.outing.id == outing.id
            assert outing_reservation_fetched.outing_id == outing.id
            assert outing_reservation_fetched.source_id == self.getstr("source_id")
            assert outing_reservation_fetched.source == RestaurantSource.GOOGLE_PLACES
            assert outing_reservation_fetched.start_time_utc == self.getdatetime("start_time_utc")
            assert outing_reservation_fetched.start_time_local == self.getdatetime("start_time_utc").astimezone(
                survey.timezone
            )
            assert outing_reservation_fetched.timezone == survey.timezone
            assert outing_reservation_fetched.headcount == survey.headcount
