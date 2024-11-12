from dataclasses import dataclass

from eave.core.graphql.types.activity import ActivitySubcategory
from eave.core.graphql.types.restaurant import RestaurantCategory


@dataclass
class UserPreferences:
    open_to_bars: bool
    requires_wheelchair_accessibility: bool
    restaurant_categories: list[RestaurantCategory]
    activity_categories: list[ActivitySubcategory]


@dataclass
class User:
    account_id: str | None
    visitor_id: str | None
    preferences: UserPreferences | None
