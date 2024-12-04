from ..base import BaseTestCase


class TestListRestaurantCategories(BaseTestCase):
    async def test_list_activity_category_groups(self) -> None:
        response = await self.make_graphql_request(
            "listRestaurantCategories",
            {},
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["restaurantCategories"]
        assert len(data) > 0

        assert data[0]["id"] is not None
        assert data[0]["name"] is not None
        assert data[0]["isDefault"] is not None
