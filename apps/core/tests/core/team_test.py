import sqlalchemy.exc

import eave.core.internal.database as eave_db
from eave.core.internal.orm.confluence_destination import ConfluenceDestinationOrm
from eave.core.internal.orm.connect_installation import ConnectInstallationOrm
from eave.core.internal.orm.team import TeamOrm
from eave.stdlib.core_api.models.connect import AtlassianProduct

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

    async def test_document_destination(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)

            connect_installation = await ConnectInstallationOrm.create(
                session=s,
                team_id=team.id,
                product=AtlassianProduct.confluence,
                client_key=self.anystring("client_key"),
                shared_secret=self.anystring("shared_secret"),
                base_url=self.anystring("base_url"),
            )
            await ConfluenceDestinationOrm.create(
                session=s,
                connect_installation_id=connect_installation.id,
                team_id=team.id,
                space_key=self.anystring("space_key"),
            )

            document_destination = await team.get_document_client(session=s)
            assert document_destination is not None
