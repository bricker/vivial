import json

import eave.core.internal.database as eave_db
import eave.core.internal.destinations.confluence as confluence_destination
import eave.core.internal.orm as eave_orm
import sqlalchemy.exc

from .base import BaseTestCase


class TestTeamOrm(BaseTestCase):
    async def test_find_one(self) -> None:
        team = await self.make_team()

        async with eave_db.get_async_session() as db_session:
            result = await eave_orm.TeamOrm.one_or_exception(session=db_session, team_id=team.id)

        assert result.id == team.id

    async def test_find_one_with_exception(self) -> None:
        with self.assertRaises(sqlalchemy.exc.NoResultFound):
            async with eave_db.get_async_session() as db_session:
                await eave_orm.TeamOrm.one_or_exception(session=db_session, team_id=self.anyuuid("teamid"))

    async def test_document_destination(self) -> None:
        team = await self.make_team()
        atlassian_installation = eave_orm.AtlassianInstallationOrm(
            team_id=team.id,
            atlassian_cloud_id=self.anystring("atlassian_cloud_id"),
            confluence_space=self.anystring("confluence_space"),
            oauth_token_encoded=json.dumps({"access_token": self.anystring()}),
        )
        await self.save(atlassian_installation)

        async with eave_db.get_async_session() as db_session:
            document_destination = await team.get_document_destination(session=db_session)

        assert document_destination is not None
        assert isinstance(document_destination, confluence_destination.ConfluenceDestination)
        assert document_destination.atlassian_cloud_id == self.anystring("atlassian_cloud_id")
        assert document_destination.space == self.anystring("confluence_space")
