import sqlalchemy.exc

import eave.core.internal.database as eave_db
from eave.core.internal.orm.team import TeamOrm, bq_dataset_id

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

    async def test_origin_not_allowed(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)
            team.allowed_origins = []

        assert not team.origin_allowed(origin=self.anyurl())

    async def test_origin_allowed(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)
            team.allowed_origins = ["dashboard.eave.fyi"]

        assert team.origin_allowed(origin="https://dashboard.eave.fyi")

    async def test_origin_allowed_with_port(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)
            team.allowed_origins = ["dashboard.eave.fyi"]

        assert team.origin_allowed(origin="https://dashboard.eave.fyi:8080")

    async def test_origin_allowed_with_wildcard(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)
            team.allowed_origins = ["*.eave.fyi"]

        assert team.origin_allowed(origin="https://dashboard.eave.fyi")

    async def test_origin_allowed_with_multi_subdomain_wildcard(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)
            team.allowed_origins = ["*.eave.fyi"]

        assert team.origin_allowed(origin="https://dashboard.internal.eave.fyi")

    async def test_origin_allowed_with_multi_subdomain_wildcard_first(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)
            team.allowed_origins = ["*.internal.eave.fyi"]

        assert team.origin_allowed(origin="https://dashboard.internal.eave.fyi")

    async def test_origin_allowed_with_full_wildcard(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)
            team.allowed_origins = ["*"]

        assert team.origin_allowed(origin=self.anyurl())

    async def test_bq_dataset_id(self):
        u = self.anyuuid()
        assert bq_dataset_id(id=u) == f"team_{u.hex}"
