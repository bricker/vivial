import http

from eave.core.internal.orm.atlassian_installation import AtlassianInstallationOrm
from eave.stdlib.atlassian import ConfluencePage
from eave.stdlib.core_api.operations import SearchDocuments
from .base import BaseTestCase


class TestSearchDocuments(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        async with self.db_session.begin() as s:
            self.testdata["eave_team"] = eave_team = await self.make_team(s)
            await AtlassianInstallationOrm.create(
                session=s,
                atlassian_cloud_id=self.anystring("atlassian_cloud_id"),
                confluence_space_key=self.anystring("confluence_space_key"),
                oauth_token_encoded=self.anyjson("oauth_token_encoded"),
                team_id=eave_team.id,
            )

    async def test_search_documents(self) -> None:
        docjson = self.confluence_document_response_fixture()

        self.get_mock("AtlassianRestAPI.get").return_value = {
            "results": [{"content": docjson}],
        }

        response = await self.make_request(
            path="/documents/search",
            payload={
                "query": self.anystring("search query"),
            },
            team_id=self.testdata["eave_team"].id,
        )

        assert response.status_code == http.HTTPStatus.OK
        response_obj = SearchDocuments.ResponseBody(**response.json())

        assert len(response_obj.documents) == 1
        expected_page = ConfluencePage(data=docjson)
        assert response_obj.documents[0].url == expected_page.canonical_url(
            self.anystring("confluence_document_response._links.base")
        )
        assert response_obj.documents[0].title == expected_page.title

    async def test_search_documents_with_confluence_error(self) -> None:
        self.get_mock("AtlassianRestAPI.get").side_effect = Exception("fake error for testing")

        response = await self.make_request(
            path="/documents/search",
            payload={
                "query": self.anystring("search query"),
            },
            team_id=self.testdata["eave_team"].id,
        )

        assert response.status_code == http.HTTPStatus.OK
        response_obj = SearchDocuments.ResponseBody(**response.json())
        assert len(response_obj.documents) == 0

    async def test_search_documents_with_bad_response(self) -> None:
        self.get_mock("AtlassianRestAPI.get").return_value = None

        response = await self.make_request(
            path="/documents/search",
            payload={
                "query": self.anystring("search query"),
            },
            team_id=self.testdata["eave_team"].id,
        )

        assert response.status_code == http.HTTPStatus.OK
        response_obj = SearchDocuments.ResponseBody(**response.json())
        assert len(response_obj.documents) == 0

    async def test_search_documents_with_no_results(self) -> None:
        self.get_mock("AtlassianRestAPI.get").return_value = {}

        response = await self.make_request(
            path="/documents/search",
            payload={
                "query": self.anystring("search query"),
            },
            team_id=self.testdata["eave_team"].id,
        )

        assert response.status_code == http.HTTPStatus.OK
        response_obj = SearchDocuments.ResponseBody(**response.json())
        assert len(response_obj.documents) == 0
