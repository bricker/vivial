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
                        search_query="created",
                    ),
                )
            ).all()

        for i in range(num_events // 2):
            assert (
                result[i].readable_name == f"Account Created {i}"
            ), "First matches were not the events containing the search term"

        async with eave_db.async_session.begin() as db_session:
            result = (
                await VirtualEventOrm.query(
                    db_session,
                    params=VirtualEventOrm.QueryParams(
                        search_query="account craeted",
                    ),
                )
            ).all()

        for i in range(num_events // 2):
            assert (
                result[i].readable_name == f"Account Created {i}"
            ), "First matches were not the best match for the mispelled search term"

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
            e4 = await VirtualEventOrm.create(
                session=s,
                team_id=team.id,
                readable_name="User was deleted2",
                description=self.anystr(),
                view_id=self.anystr(),
            )
            e5 = await VirtualEventOrm.create(
                session=s,
                team_id=team.id,
                readable_name="User was deleted1",
                description=self.anystr(),
                view_id=self.anystr(),
            )
            await VirtualEventOrm.create(
                session=s,
                team_id=team.id,
                readable_name="User was created",  # This one should fall below the threshold
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
        assert result[2].id == e3.id, "query result events were out of order"
        assert result[1].id == e2.id, "query result events were out of order"

        async with eave_db.async_session.begin() as db_session:
            result = (
                await VirtualEventOrm.query(
                    db_session,
                    params=VirtualEventOrm.QueryParams(
                        search_query="User was deleted2",
                    ),
                )
            ).all()

        assert len(result) == 2
        assert result[0].id == e4.id, "best match was not first result"
        assert result[1].id == e5.id, "best match was not first result"
