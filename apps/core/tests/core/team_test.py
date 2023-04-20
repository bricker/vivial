import eave.core.internal.destinations.confluence as confluence_destination
import eave.core.internal.orm as eave_orm
import eave.stdlib.core_api.models as eave_models
import sqlalchemy.exc

from .base import BaseTestCase


class TestTeamOrm(BaseTestCase):
    async def test_find_one(self) -> None:
        team = eave_orm.TeamOrm(
            name=self.anystring("teamname"), document_platform=eave_models.DocumentPlatform.confluence
        )
        await self.save(team)

        result = await eave_orm.TeamOrm.one_or_exception(session=self.dbsession, team_id=team.id)
        self.assertEqual(self.unwrap(result), team)

    async def test_find_one_with_exception(self) -> None:
        with self.assertRaises(sqlalchemy.exc.NoResultFound):
            await eave_orm.TeamOrm.one_or_exception(session=self.dbsession, team_id=self.anyuuid("teamid"))

    async def test_document_destination(self) -> None:
        team = eave_orm.TeamOrm(
            name=self.anystring("teamname"), document_platform=eave_models.DocumentPlatform.confluence
        )
        await self.save(team)

        document_destination = await team.get_document_destination(session=self.dbsession)
        self.assertIsInstance(document_destination, confluence_destination.ConfluenceDestination)
