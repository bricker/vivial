import sqlalchemy.exc

import eave.core.internal.database as eave_db
from eave.core.internal.orm.team import TeamOrm
from eave.core.internal.orm.virtual_event import VirtualEventOrm

from .base import BaseTestCase


class TestVirtualEventOrm(BaseTestCase):
    async def test_search_query(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)
            virtual_event = await VirtualEventOrm.create(
                session=s,
                team_id=team.id,
                readable_name="Account Created",
                description=self.anystr(),
                view_id=self.anystr(),
            )

        async with eave_db.async_session.begin() as db_session:
            result = (await VirtualEventOrm.query(db_session, params=VirtualEventOrm.QueryParams(
                search_query="Account",
            ))).all()

        assert result[0].id == virtual_event.id


    async def test_find_one_with_exception(self) -> None:
        with self.assertRaises(sqlalchemy.exc.NoResultFound):
            async with eave_db.async_session.begin() as db_session:
                await TeamOrm.one_or_exception(session=db_session, team_id=self.anyuuid("teamid"))
