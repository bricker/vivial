import unittest.mock
import eave.core.internal.destinations.confluence as confluence_destination
import eave.core.internal.oauth.atlassian as atlassian_oauth
from eave.core.internal.orm.document_reference import DocumentReferenceOrm
from eave.stdlib.core_api.models.documents import DocumentInput

from .base import BaseTestCase


class TestConfluenceDestination(BaseTestCase):
    async def test_create_document(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)

            oauth_session = atlassian_oauth.AtlassianOAuthSession()

            destination = confluence_destination.ConfluenceDestination(
                atlassian_cloud_id=self.anystring("atlassian_cloud_id"),
                space=self.anystring("space"),
                oauth_session=oauth_session,
            )

            document_reference = DocumentReferenceOrm(
                team_id=team.id,
                document_id=self.anystring("confluence_document_response.id"),
                document_url=self.anystring("cdurl"),
            )
            await self.save(s, document_reference)

            self.patch(unittest.mock.patch("atlassian.Confluence.get_page_by_title", return_value=None))
            self.patch(
                unittest.mock.patch(
                    "atlassian.Confluence.create_page", return_value=self.confluence_document_response_fixture()
                )
            )

            input = DocumentInput(
                title=self.anystring("doctitle"),
                content=self.anystring("doccontent"),
            )
            document_metadata = await destination.create_document(input=input)
            assert document_metadata.id == self.anystring("confluence_document_response.id")
            assert document_metadata.url == (
                self.anystring("confluence_document_response._links.base")
                + "/wiki/"
                + self.anystring("confluence_document_response._links.tinyui")
            )
