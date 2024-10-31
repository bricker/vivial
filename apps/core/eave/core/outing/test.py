import asyncio
from datetime import datetime

from models.category import Category
from models.search_region_code import SearchRegionCode
from models.user import User, UserPreferences

from eave.core.internal.orm.survey import SurveyOrm
from eave.core.outing import Outing


# TODO: Write thorough automated tests once all relevant tables / endpoints are ready (pending Bryan).
async def main() -> None:
    test_outing_constraints = SurveyOrm(
        start_time=datetime.fromisoformat("2024-10-25T19:42:31.946205"),
        search_area_ids=[SearchRegionCode.US_CA_LA2],
        budget=2,
        headcount=2,
    )
    test_category_1 = Category(id="103", subcategory_id="3008")
    test_category_2 = Category(id="103", subcategory_id="3012")
    test_category_3 = Category(id="105", subcategory_id="5001")
    test_category_4 = Category(id="103", subcategory_id="3008")
    test_category_5 = Category(id="103", subcategory_id="3013")
    test_category_6 = Category(id="104", subcategory_id="4007")
    test_user_1 = User(
        id=None,
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
                activity_categories=[test_category_1, test_category_2, test_category_3],
            )
        ),
    )
    test_user_2 = User(
        id="",
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
                activity_categories=[test_category_4, test_category_5, test_category_6],
            )
        ),
    )

    test_outing = Outing([test_user_1, test_user_2], test_outing_constraints)
    test_outing_plan = await test_outing.plan()

    if test_outing_plan.restaurant and test_outing_plan.restaurant.external_details and test_outing_plan:
        if test_restaurant_name := test_outing_plan.restaurant.external_details.get("displayName"):
            print(f"Dinner at {test_restaurant_name.get("text")}")

    if test_outing_plan.activity and test_outing_plan.activity.external_details:
        if test_activity_name := test_outing_plan.activity.external_details.get("displayName"):
            print(f"then hang at {test_activity_name.get("text")}.")


if __name__ == "__main__":
    asyncio.run(main())
