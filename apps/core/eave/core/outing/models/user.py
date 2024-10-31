from dataclasses import dataclass

from .category import Category


@dataclass
class UserPreferences:
    open_to_bars: bool
    requires_wheelchair_accessibility: bool
    restaurant_categories: list[Category]
    activity_categories: list[Category]


@dataclass
class User:
    id: str | None
    visitor_id: str | None
    preferences: UserPreferences | None
