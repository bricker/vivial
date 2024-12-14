from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.outing_preferences import OutingPreferencesOrm
from eave.core.orm.restaurant_category import RestaurantCategoryOrm

from ..base import BaseTestCase


class TestGetOutingPreferences(BaseTestCase):
    async def test_outing_preferences_with_selected(self) -> None:
        first_restaurant_category = RestaurantCategoryOrm.all()[0]
        first_activity_category = ActivityCategoryOrm.all()[0]

        async with self.db_session.begin() as session:
            account = self.make_account(session)

            OutingPreferencesOrm(
                session,
                account=account,
                activity_category_ids=[first_activity_category.id],
                restaurant_category_ids=[first_restaurant_category.id],
            )

        response = await self.make_graphql_request(
            "getOutingPreferences",
            {},
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["outingPreferences"]

        assert len(data["restaurantCategories"]) == 1
        assert data["restaurantCategories"][0]["id"] == str(first_restaurant_category.id)

        assert len(data["activityCategories"]) == 1
        assert data["activityCategories"][0]["id"] == str(first_activity_category.id)

    async def test_outing_preferences_with_none_selected(self) -> None:
        async with self.db_session.begin() as db_session:
            account = self.make_account(db_session)

        response = await self.make_graphql_request(
            "getOutingPreferences",
            {},
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["outingPreferences"]

        assert data["restaurantCategories"] is None
        assert data["activityCategories"] is None

    async def test_outing_preferences_with_none_values(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)

            OutingPreferencesOrm(
                session,
                account=account,
                activity_category_ids=None,
                restaurant_category_ids=None,
            )

        response = await self.make_graphql_request(
            "getOutingPreferences",
            {},
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["outingPreferences"]

        assert data["restaurantCategories"] is None
        assert data["activityCategories"] is None
