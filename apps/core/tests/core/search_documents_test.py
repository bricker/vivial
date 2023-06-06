import http
import unittest.mock

from eave.core.internal.orm.confluence_destination import ConfluenceDestinationOrm
from eave.core.internal.orm.connect_installation import ConnectInstallationOrm
from eave.stdlib.atlassian import ConfluencePage
from eave.stdlib.core_api.models.connect import AtlassianProduct, RegisterConnectInstallationInput
from eave.stdlib.core_api.operations.documents import SearchDocuments
from .base import BaseTestCase


class TestSearchDocuments(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        async with self.db_session.begin() as s:
            self.testdata["eave_team"] = await self.make_team(s)
            connect = await ConnectInstallationOrm.create(
                session=s,
                team_id=self.testdata["eave_team"].id,
                input=RegisterConnectInstallationInput.parse_obj(
                    {
                        "product": AtlassianProduct.confluence,
                        "client_key": self.anystring("client_key"),
                        "base_url": self.anystring("base_url"),
                        "shared_secret": self.anystring("shared_secret"),
                    }
                ),
            )

            await ConfluenceDestinationOrm.create(
                session=s,
                connect_installation_id=connect.id,
                team_id=self.testdata["eave_team"].id,
                space_key=self.anystring("space_key"),
            )

            self._request_mock = self.patch(
                name="SearchContentRequest",
                patch=unittest.mock.patch("eave.stdlib.confluence_api.operations.SearchContentRequest.perform"),
            )

    async def test_search_documents(self) -> None:
        docjson = self.confluence_document_response_fixture()

        self.get_mock("SearchContentRequest").return_value = {
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
        self.get_mock("SearchContentRequest").side_effect = Exception("fake error for testing")

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
        self.get_mock("SearchContentRequest").return_value = None

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
        self.get_mock("SearchContentRequest").return_value = {}

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
