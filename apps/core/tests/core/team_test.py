import sqlalchemy.exc

import eave.core.internal.database as eave_db
from eave.core.internal.orm.team import TeamOrm

from .base import BaseTestCase


class TestTeamOrm(BaseTestCase):
    async def test_find_one(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)

        async with eave_db.async_session.begin() as db_session:
            result = await TeamOrm.one_or_exception(session=db_session, team_id=team.id)

        assert result.id == team.id

    async def test_find_one_with_exception(self) -> None:
        with self.assertRaises(sqlalchemy.exc.NoResultFound):
            async with eave_db.async_session.begin() as db_session:
                await TeamOrm.one_or_exception(session=db_session, team_id=self.anyuuid("teamid"))
