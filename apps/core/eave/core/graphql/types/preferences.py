from uuid import UUID
import strawberry

from eave.core.graphql.types.activity import ActivityCategory
from eave.core.graphql.types.restaurant import RestaurantCategory


@strawberry.type
class Preferences:
    open_to_bars: bool
    requires_wheelchair_accessibility: bool
    restaurant_categories: list[RestaurantCategory]
    activity_categories: list[ActivityCategory]


@strawberry.input
class PreferencesInput:
    open_to_bars: bool
    requires_wheelchair_accessibility: bool
    restaurant_category_ids: list[UUID]
    activity_category_ids: list[UUID]
