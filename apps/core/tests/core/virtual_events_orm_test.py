import sqlalchemy.exc

import eave.core.internal.database as eave_db
from eave.core.internal.orm.team import TeamOrm
from eave.core.internal.orm.virtual_event import VirtualEventOrm

from .base import BaseTestCase


class TestVirtualEventOrm(BaseTestCase):
    async def test_search_query_result_quantities(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)

            num_events = 10
            mid = num_events // 2
            for i in range(1, num_events + 1):
                verb = "Created" if i <= mid else "Updated"
                await VirtualEventOrm.create(
                    session=s,
                    team_id=team.id,
                    readable_name=f"Account {verb} {i % mid}",
                    description=self.anystr(),
                    view_id=self.anystr(),
                )

        async with eave_db.async_session.begin() as db_session:
            result = (
                await VirtualEventOrm.query(
                    db_session,
                    params=VirtualEventOrm.QueryParams(
                        search_query="Account",
                    ),
                )
            ).all()

        assert len(result) == num_events, "prefix did not capture all events"

        async with eave_db.async_session.begin() as db_session:
            result = (
                await VirtualEventOrm.query(
                    db_session,
                    params=VirtualEventOrm.QueryParams(
                        search_query="created",
                    ),
                )
            ).all()

        assert len(result) == num_events // 2, "partial match results not found"

        async with eave_db.async_session.begin() as db_session:
            result = (
                await VirtualEventOrm.query(
                    db_session,
                    params=VirtualEventOrm.QueryParams(
                        search_query="account craeted",
                    ),
                )
            ).all()

        assert len(result) == num_events // 2, "mispelling not corrected by fuzzy match"

    async def test_find_one_with_exception(self) -> None:
        with self.assertRaises(sqlalchemy.exc.NoResultFound):
            async with eave_db.async_session.begin() as db_session:
                await TeamOrm.one_or_exception(session=db_session, team_id=self.anyuuid("teamid"))

    async def test_search_query_order(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)

            e1 = await VirtualEventOrm.create(
                session=s,
                team_id=team.id,
                readable_name="Account create",
                description=self.anystr(),
                view_id=self.anystr(),
            )
            e3 = await VirtualEventOrm.create(
                session=s,
                team_id=team.id,
                readable_name="Account creation completed",
                description=self.anystr(),
                view_id=self.anystr(),
            )
            await VirtualEventOrm.create(
                session=s,
                team_id=team.id,
                readable_name="Account was deleted1",
                description=self.anystr(),
                view_id=self.anystr(),
            )
            await VirtualEventOrm.create(
                session=s,
                team_id=team.id,
                readable_name="Account was deleted2",
                description=self.anystr(),
                view_id=self.anystr(),
            )
            e2 = await VirtualEventOrm.create(
                session=s,
                team_id=team.id,
                readable_name="Account created today",
                description=self.anystr(),
                view_id=self.anystr(),
            )

        async with eave_db.async_session.begin() as db_session:
            result = (
                await VirtualEventOrm.query(
                    db_session,
                    params=VirtualEventOrm.QueryParams(
                        search_query="account cre",
                    ),
                )
            ).all()

        assert len(result) == 3, "query returned incorrect number of results"
        assert result[0].id == e1.id, "query result events were out of order"
        assert result[1].id == e2.id, "query result events were out of order"
        assert result[2].id == e3.id, "query result events were out of order"

        async with eave_db.async_session.begin() as db_session:
            result = (
                await VirtualEventOrm.query(
                    db_session,
                    params=VirtualEventOrm.QueryParams(
                        search_query="Account was deleted2",
                    ),
                )
            ).all()

        assert len(result) >= 1
        assert result[0].readable_name == "Account was deleted2", "exact match was not first result"
