from dataclasses import dataclass

from .category import ActivityCategory, ActivitySubcategory, Category


@dataclass
class UserPreferences:
    open_to_bars: bool
    requires_wheelchair_accessibility: bool
    restaurant_categories: list[Category]
    activity_categories: list[ActivitySubcategory]


@dataclass
class User:
    id: str | None
    visitor_id: str | None
    preferences: UserPreferences
