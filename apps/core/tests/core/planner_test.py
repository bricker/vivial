import asyncio
import uuid
from datetime import datetime

from eave.core.graphql.resolvers.mutations.helpers.planner import OutingPlanner
from eave.core.graphql.types.activity import ActivityCategoryGroup
from eave.core.graphql.types.outing_preferences import OutingPreferences
from eave.core.graphql.types.restaurant import RestaurantCategory
from eave.core.graphql.types.survey import Survey
from eave.core.orm.activity_category_group import _ACTIVITY_CATEGORY_GROUPS_TABLE
from eave.core.orm.restaurant_category import _RESTAURANT_CATEGORIES_TABLE
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.shared.enums import OutingBudget


# TODO: Write thorough automated tests once all relevant tables / endpoints are ready (pending Bryan).
async def main() -> None:
    test_outing_constraints = Survey(
        id=uuid.uuid4(),
        visitor_id=uuid.uuid4(),
        start_time=datetime.fromisoformat("2024-10-25T19:42:31.946205"),
        search_area_ids=[SearchRegionOrm.all()[0].id],
        budget=OutingBudget.INEXPENSIVE,
        headcount=2,
    )
    test_preferences1 = OutingPreferences(
        open_to_bars=True,
        requires_wheelchair_accessibility=False,
        restaurant_categories=[RestaurantCategory.from_orm(cat) for cat in _RESTAURANT_CATEGORIES_TABLE[0:3]],
        activity_categories=[ActivityCategoryGroup.from_orm(cat) for cat in _ACTIVITY_CATEGORY_GROUPS_TABLE[0:3]],
    )

    test_preferences2 = OutingPreferences(
        open_to_bars=True,
        requires_wheelchair_accessibility=False,
        restaurant_categories=[RestaurantCategory.from_orm(cat) for cat in _RESTAURANT_CATEGORIES_TABLE[3:6]],
        activity_categories=[ActivityCategoryGroup.from_orm(cat) for cat in _ACTIVITY_CATEGORY_GROUPS_TABLE[3:6]],
    )

    test_outing = OutingPlanner([test_preferences1, test_preferences2], test_outing_constraints)
    test_outing_plan = await test_outing.plan()
    test_restaurant = test_outing_plan.restaurant and test_outing_plan.restaurant
    test_activity = test_outing_plan.activity and test_outing_plan.activity

    if test_restaurant and test_restaurant.name:
        print(f"Dinner at {test_restaurant.name}")

    if test_activity and test_activity.name:
        print(f"then hang at {test_activity.name}.")


if __name__ == "__main__":
    asyncio.run(main())
