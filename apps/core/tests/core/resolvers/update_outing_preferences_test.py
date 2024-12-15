from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.outing_preferences import OutingPreferencesOrm
from eave.core.orm.restaurant_category import RestaurantCategoryOrm

from ..base import BaseTestCase


class TestUpdateOutingPreferences(BaseTestCase):
    async def test_update_outing_preferences_with_existing_preferences(self) -> None:
        first_restaurant_category = RestaurantCategoryOrm.all()[0]
        second_restaurant_category = RestaurantCategoryOrm.all()[1]
        first_activity_category = ActivityCategoryOrm.all()[0]
        second_activity_category = ActivityCategoryOrm.all()[1]

        async with self.db_session.begin() as session:
            account = self.make_account(session)
            outing_preferences_orm = OutingPreferencesOrm(
                session,
                account=account,
                activity_category_ids=[first_activity_category.id],
                restaurant_category_ids=[first_restaurant_category.id],
            )

        response = await self.make_graphql_request(
            "updateOutingPreferences",
            {
                "input": {
                    "activityCategoryIds": [str(first_activity_category.id), str(second_activity_category.id)],
                    "restaurantCategoryIds": [str(first_restaurant_category.id), str(second_restaurant_category.id)],
                }
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["updateOutingPreferences"]["outingPreferences"]

        assert len(data["restaurantCategories"]) == 2
        assert data["restaurantCategories"][0]["id"] == str(first_restaurant_category.id)
        assert data["restaurantCategories"][1]["id"] == str(second_restaurant_category.id)

        assert len(data["activityCategories"]) == 2
        assert data["activityCategories"][0]["id"] == str(first_activity_category.id)
        assert data["activityCategories"][1]["id"] == str(second_activity_category.id)

        async with self.db_session.begin() as session:
            outing_preferences_orm = await OutingPreferencesOrm.get_one(
                session, account_id=account.id, uid=outing_preferences_orm.id
            )
            assert outing_preferences_orm.activity_category_ids == [
                first_activity_category.id,
                second_activity_category.id,
            ]
            assert outing_preferences_orm.restaurant_category_ids == [
                first_restaurant_category.id,
                second_restaurant_category.id,
            ]

    async def test_update_outing_preferences_without_existing_preferences(self) -> None:
        first_restaurant_category = RestaurantCategoryOrm.all()[0]
        first_activity_category = ActivityCategoryOrm.all()[0]

        async with self.db_session.begin() as db_session:
            account = self.make_account(db_session)
            outing_preferences_orm = (
                await db_session.scalars(OutingPreferencesOrm.select(account_id=account.id))
            ).one_or_none()
            assert outing_preferences_orm is None

        response = await self.make_graphql_request(
            "updateOutingPreferences",
            {
                "input": {
                    "activityCategoryIds": [str(first_activity_category.id)],
                    "restaurantCategoryIds": [str(first_restaurant_category.id)],
                }
            },
            account_id=account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["updateOutingPreferences"]["outingPreferences"]

        assert len(data["restaurantCategories"]) == 1
        assert data["restaurantCategories"][0]["id"] == str(first_restaurant_category.id)

        assert len(data["activityCategories"]) == 1
        assert data["activityCategories"][0]["id"] == str(first_activity_category.id)

        async with self.db_session.begin() as db_session:
            outing_preferences_orm = (
                await db_session.scalars(OutingPreferencesOrm.select(account_id=account.id))
            ).one()
            assert outing_preferences_orm.activity_category_ids == [first_activity_category.id]
            assert outing_preferences_orm.restaurant_category_ids == [first_restaurant_category.id]
