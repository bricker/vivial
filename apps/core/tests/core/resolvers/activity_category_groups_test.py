from httpx import Response

from eave.core.auth_cookies import ACCESS_TOKEN_COOKIE_NAME, REFRESH_TOKEN_COOKIE_NAME
from eave.core.orm.account import AccountOrm

from ..base import BaseTestCase


class TestListActivityCategoryGroups(BaseTestCase):
    async def test_list_activity_category_groups(self) -> None:
        response = await self.make_graphql_request(
            "listActivityCategoryGroups",
            {},
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["activityCategoryGroups"]
        first_group = data[0]

        assert first_group["id"] is not None
        assert first_group["name"] is not None
        assert len(first_group["activityCategories"]) > 0

        assert first_group["activityCategories"][0]["id"] is not None
        assert first_group["activityCategories"][0]["name"] is not None
        assert first_group["activityCategories"][0]["isDefault"] is not None
