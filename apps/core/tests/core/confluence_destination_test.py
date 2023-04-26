import atlassian
import eave.core.internal.destinations.confluence as confluence_destination
import eave.core.internal.oauth.atlassian as atlassian_oauth
import eave.core.internal.orm as eave_orm
import eave.stdlib.core_api.operations as eave_ops
import mockito

from . import fixtures
from .base import BaseTestCase


class TestConfluenceDestination(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        self.team = await self.make_team()
        oauth_session = atlassian_oauth.AtlassianOAuthSession()
        mockito.when2(oauth_session.get_available_resources).thenReturn(
            [
                atlassian_oauth.AtlassianAvailableResource(
                    id=self.anystring("atlassian_cloud_id"),
                    url=self.anystring("confluence_document_response._links.base"),
                    avatarUrl=self.anystring("atlassianresourceavatar"),
                    name=self.anystring("atlassianresourcename"),
                    scopes=[],
                )
            ]
        )

        self.confluence_destination = confluence_destination.ConfluenceDestination(
            atlassian_cloud_id=self.anystring("atlassian_cloud_id"),
            space=self.anystring("space"),
            oauth_session=oauth_session,
        )

        document_reference = eave_orm.DocumentReferenceOrm(
            team_id=self.team.id,
            document_id=self.anystring("confluence_document_response.id"),
            document_url=self.anystring("cdurl"),
        )
        self.document_reference = await self.save(document_reference)

    async def test_create_document(self) -> None:
        mockito.when2(atlassian.Confluence.get_page_by_title, **mockito.KWARGS).thenReturn(None)
        mockito.when2(atlassian.Confluence.create_page, **mockito.KWARGS).thenReturn(
            fixtures.confluence_document_response(self)
        )

        input = eave_ops.DocumentInput(
            title=self.anystring("doctitle"),
            content=self.anystring("doccontent"),
        )
        document_metadata = await self.confluence_destination.create_document(input=input)
        self.assertEqual(document_metadata.id, self.anystring("confluence_document_response.id"))
        self.assertEqual(
            document_metadata.url,
            self.anystring("confluence_document_response._links.base")
            + "/wiki/"
            + self.anystring("confluence_document_response._links.tinyui"),
        )
