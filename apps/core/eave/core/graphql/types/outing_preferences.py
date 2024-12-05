import strawberry

from eave.core.graphql.types.activity import ActivityCategory
from eave.core.graphql.types.restaurant import RestaurantCategory
from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.outing_preferences import OutingPreferencesOrm
from eave.core.orm.restaurant_category import RestaurantCategoryOrm


@strawberry.type
class OutingPreferences:
    open_to_bars: bool | None
    restaurant_categories: list[RestaurantCategory] | None
    activity_categories: list[ActivityCategory] | None

    @classmethod
    def from_orm(cls, orm: OutingPreferencesOrm) -> "OutingPreferences":
        restaurant_categories: list[RestaurantCategory] | None = None
        if orm.restaurant_category_ids is not None:
            restaurant_categories = []
            for restaurant_category_id in orm.restaurant_category_ids:
                if restaurant_category_orm := RestaurantCategoryOrm.one_or_none(
                    restaurant_category_id=restaurant_category_id
                ):
                    restaurant_categories.append(RestaurantCategory.from_orm(restaurant_category_orm))

        activity_categories: list[ActivityCategory] | None = None
        if orm.activity_category_ids is not None:
            activity_categories = []
            for activity_category_id in orm.activity_category_ids:
                if activity_category_orm := ActivityCategoryOrm.one_or_none(activity_category_id=activity_category_id):
                    activity_categories.append(ActivityCategory.from_orm(activity_category_orm))

        if orm.open_to_bars is None:
            open_to_bars = True  # Default value
        else:
            open_to_bars = orm.open_to_bars

        return OutingPreferences(
            open_to_bars=open_to_bars,
            restaurant_categories=restaurant_categories,
            activity_categories=activity_categories,
        )
