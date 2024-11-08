import asyncio
from datetime import datetime

from models.category import Category
from models.outing import OutingConstraints
from models.user import User, UserPreferences

from eave.core.graphql.types.search_region import SearchRegionCode
from eave.core.outing.constants.categories import ACTIVITY_SUBCATEGORIES
from eave.core.outing.planner import OutingPlanner


# TODO: Write thorough automated tests once all relevant tables / endpoints are ready (pending Bryan).
async def main() -> None:
    test_outing_constraints = OutingConstraints(
        start_time=datetime.fromisoformat("2024-10-25T19:42:31.946205"),
        search_area_ids=[SearchRegionCode.US_CA_LA2],
        budget=2,
        headcount=2,
    )
    test_user_1 = User(
        account_id=None,
        visitor_id=None,
        preferences=(
            UserPreferences(
                open_to_bars=True,
                requires_wheelchair_accessibility=False,
                restaurant_categories=[
                    Category(id="sushi_restaurant"),
                    Category(id="american_restaurant"),
                    Category(id="brazilian_restaurant"),
                ],
                activity_categories=ACTIVITY_SUBCATEGORIES[0:3],
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
                restaurant_categories=[
                    Category(id="chinese_restaurant"),
                    Category(id="fast_food_restaurant"),
                    Category(id="mexican_restaurant"),
                ],
                activity_categories=ACTIVITY_SUBCATEGORIES[3:6],
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
