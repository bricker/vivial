import sqlalchemy.exc

import eave.core.internal.database as eave_db
import eave.core.internal.destinations.confluence as confluence_destination
import eave.core.internal.orm.atlassian_installation
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

    async def test_document_destination(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)

            atlassian_installation = eave.core.internal.orm.atlassian_installation.AtlassianInstallationOrm(
                team_id=team.id,
                atlassian_cloud_id=self.anystring("atlassian_cloud_id"),
                confluence_space_key=self.anystring("confluence_space"),
                oauth_token_encoded=self.anyjson("oauth_token_encoded"),
            )
            await self.save(s, atlassian_installation)

            document_destination = await team.get_document_destination(session=s)

            assert document_destination is not None
            assert isinstance(document_destination, confluence_destination.ConfluenceDestination)
            assert document_destination.atlassian_cloud_id == self.anystring("atlassian_cloud_id")
            assert document_destination.space == self.anystring("confluence_space")
