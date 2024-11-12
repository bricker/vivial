import asyncio
from datetime import datetime

from eave.core.graphql.types.activity import ActivityCategory, ActivitySubcategory
from eave.core.graphql.types.restaurant import RestaurantCategory
from eave.core.orm.activity_subcategory import _ACTIVITY_SUBCATEGORIES_PK, _ACTIVITY_SUBCATEGORIES_TABLE
from eave.core.orm.restaurant_category import _RESTAURANT_CATEGORIES_PK, _RESTAURANT_CATEGORIES_TABLE
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.orm.survey import SurveyOrm
from models.user import User, UserPreferences

from eave.core.graphql.types.outing import OutingBudget
from eave.core.outing.planner import OutingPlanner


# TODO: Write thorough automated tests once all relevant tables / endpoints are ready (pending Bryan).
async def main() -> None:
    test_outing_constraints = SurveyOrm(
        start_time=datetime.fromisoformat("2024-10-25T19:42:31.946205"),
        search_area_ids=[SearchRegionOrm.all()[0].id],
        budget=OutingBudget.TWO,
        headcount=2,
    )
    test_user_1 = User(
        account_id=None,
        visitor_id=None,
        preferences=(
            UserPreferences(
                open_to_bars=True,
                requires_wheelchair_accessibility=False,
                restaurant_categories=[RestaurantCategory.from_orm(cat) for cat in _RESTAURANT_CATEGORIES_TABLE[0:3]],
                activity_categories=[ActivitySubcategory.from_orm(cat) for cat in _ACTIVITY_SUBCATEGORIES_TABLE[0:3]],
            )
        ),
    )
    test_user_2 = User(
        account_id="",
        visitor_id="",
        preferences=(
            UserPreferences(
                open_to_bars=True,
                requires_wheelchair_accessibility=False,
                restaurant_categories=[RestaurantCategory.from_orm(cat) for cat in _RESTAURANT_CATEGORIES_TABLE[3:6]],
                activity_categories=[ActivitySubcategory.from_orm(cat) for cat in _ACTIVITY_SUBCATEGORIES_TABLE[3:6]],
            )
        ),
    )

    test_outing = OutingPlanner([test_user_1, test_user_2], test_outing_constraints)
    test_outing_plan = await test_outing.plan()
    test_restaurant = test_outing_plan.restaurant and test_outing_plan.restaurant.place
    test_activity = test_outing_plan.activity and test_outing_plan.activity.place

    if test_restaurant and test_restaurant.display_name:
        print(f"Dinner at {test_restaurant.display_name.text}")

    if test_activity and test_activity.display_name:
        print(f"then hang at {test_activity.display_name.text}.")


if __name__ == "__main__":
    asyncio.run(main())
