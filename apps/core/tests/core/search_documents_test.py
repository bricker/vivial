import http
import unittest.mock

from eave.core.internal.orm.confluence_destination import ConfluenceDestinationOrm
from eave.core.internal.orm.connect_installation import ConnectInstallationOrm
from eave.stdlib.confluence_api.models import (
    ConfluenceContentBody,
    ConfluenceContentBodyRepresentation,
    ConfluenceContentStatus,
    ConfluenceContentType,
    ConfluenceGenericLinks,
    ConfluencePageBody,
    ConfluenceSearchResultWithBody,
)
from eave.stdlib.confluence_api.operations import SearchContentRequest
from eave.stdlib.core_api.models.connect import AtlassianProduct
from eave.stdlib.core_api.operations.documents import SearchDocuments
from .base import BaseTestCase


class TestSearchDocuments(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        async with self.db_session.begin() as s:
            self.data_team = await self.make_team(s)
            connect = await ConnectInstallationOrm.create(
                session=s,
                team_id=self.data_team.id,
                product=AtlassianProduct.confluence,
                client_key=self.anystring("client_key"),
                base_url=self.anystring("base_url"),
                shared_secret=self.anystring("shared_secret"),
            )

            await ConfluenceDestinationOrm.create(
                session=s,
                connect_installation_id=connect.id,
                team_id=self.data_team.id,
                space_key=self.anystring("space_key"),
            )

            self._request_mock = self.patch(
                name="SearchContentRequest",
                patch=unittest.mock.patch("eave.stdlib.confluence_api.operations.SearchContentRequest.perform"),
            )

    async def test_search_documents(self) -> None:
        self.get_mock("SearchContentRequest").return_value = SearchContentRequest.ResponseBody(
            results=[
                ConfluenceSearchResultWithBody(
                    id=self.anystr("doc id"),
                    type=ConfluenceContentType.page,
                    status=ConfluenceContentStatus.current,
                    title=self.anystr("doc title"),
                    body=ConfluencePageBody(
                        storage=ConfluenceContentBody(
                            value=self.anystr("doc body"),
                            representation=ConfluenceContentBodyRepresentation.storage,
                            embeddedContent=None,
                            mediaToken=None,
                            webresource=None,
                        ),
                    ),
                    _links=ConfluenceGenericLinks(
                        webui=self.anypath("doc webui path"),
                        base=None,
                        collection=None,
                        context=None,
                        editui=None,
                        self=None,
                        tinyui=None,
                    ),
                ),
            ],
        )

        response = await self.make_request(
            path="/documents/search",
            payload={
                "query": self.anystring("search query"),
            },
            team_id=self.data_team.id,
        )

        assert response.status_code == http.HTTPStatus.OK
        response_obj = SearchDocuments.ResponseBody(**response.json())

        assert len(response_obj.documents) == 1
        assert response_obj.documents[0].url == self.geturl("base_url") + self.getpath("doc webui path")
        assert response_obj.documents[0].title == self.getstr("doc title")

    async def test_search_documents_with_no_results(self) -> None:
        self.get_mock("SearchContentRequest").return_value = SearchContentRequest.ResponseBody(results=[])

        response = await self.make_request(
            path="/documents/search",
            payload={
                "query": self.anystring("search query"),
            },
            team_id=self.data_team.id,
        )

        assert response.status_code == http.HTTPStatus.OK
        response_obj = SearchDocuments.ResponseBody(**response.json())
        assert len(response_obj.documents) == 0
