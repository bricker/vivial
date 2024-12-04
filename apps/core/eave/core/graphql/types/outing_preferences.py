from typing import Sequence
from uuid import UUID

import strawberry

from eave.core.graphql.types.activity import ActivityCategory, ActivityCategoryGroup
from eave.core.graphql.types.restaurant import RestaurantCategory
from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.outing_category_preference import OutingCategoryPreferenceOrm
from eave.core.orm.restaurant_category import RestaurantCategoryOrm


@strawberry.type
class OutingPreferences:
    restaurant_categories: list[RestaurantCategory]
    activity_categories: list[ActivityCategory]

    @classmethod
    def from_orms(cls, orms: Sequence[OutingCategoryPreferenceOrm]) -> "OutingPreferences":
        return OutingPreferences(
            restaurant_categories=[RestaurantCategory.from_orm(RestaurantCategoryOrm.one_or_exception(restaurant_category_id=category_preference.category_id)) for category_preference in orms if category_preference.category_type == "restaurant"],
            activity_categories=[ActivityCategory.from_orm(ActivityCategoryOrm.one_or_exception(activity_category_id=category_preference.category_id)) for category_preference in orms if category_preference.category_type == "activity"],
        )
