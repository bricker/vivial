from dataclasses import dataclass
from datetime import datetime

@dataclass
class OutingPlan:
    activity: object # TODO: Activity Schema
    restaurant: object # TODO: Restauraunt Schema

@dataclass
class OutingConstraints:
    start_time: datetime
    search_area_ids: list[str]
    budget: int
    headcount: int

@dataclass
class RestaurantCategory:
    id: str

@dataclass
class ActivityCategory:
    id: str
    subcategory_id: str

@dataclass
class UserPreferences:
    open_to_bars: bool
    requires_wheelchair_accessibility: bool
    restaurant_categories: list[RestaurantCategory]
    activity_categories: list[ActivityCategory]

@dataclass
class User:
    id: str | None
    visitor_id: str | None
    preferences: UserPreferences
