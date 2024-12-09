from eave.core.orm.search_region import SearchRegionOrm

from ..base import BaseTestCase


class TestSearchRegionsResolver(BaseTestCase):
    async def test_list_search_regions(self) -> None:
        response = await self.make_graphql_request(
            "listSearchRegions",
            {},
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["searchRegions"]

        all_search_regions = SearchRegionOrm.all()
        assert data[0]["id"] == str(all_search_regions[0].id)
        assert data[0]["name"] == all_search_regions[0].name
