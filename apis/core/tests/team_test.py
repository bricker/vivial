import eave.internal.orm as orm
import tests
from eave.public.shared import DocumentPlatform
from tests.base import BaseTestCase


class TestTeamOrm(BaseTestCase):
    async def test_find_one(self) -> None:
        team = orm.TeamOrm(name="Test Org", document_platform=DocumentPlatform.confluence)
        await self.save(team)

        result = await orm.TeamOrm.find_one(session=self.dbsession, team_id=team.id)
        self.assertEqual(self.unwrap(result), team)

    async def test_document_destination(self) -> None:
        team = orm.TeamOrm(name="Test Org", document_platform=DocumentPlatform.confluence)
        await self.save(team)

        confluence_destination = orm.ConfluenceDestinationOrm(
            team_id=team.id,
            url="https://eave-fyi.atlassian.org/wiki",
            api_username="eave@eave.fyi",
            api_key="xxx",
            space="EAVE",
        )
        await self.save(confluence_destination)

        document_destination = await team.get_document_destination(self.dbsession)
        self.assertIsInstance(document_destination, orm.ConfluenceDestinationOrm)
        self.assertEqual(document_destination, confluence_destination)
