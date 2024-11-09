from dataclasses import dataclass

from .category import ActivitySubcategory, RestaurantCategory


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
    preferences: UserPreferences
