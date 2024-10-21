from dataclasses import dataclass
from datetime import datetime

@dataclass
class OutingPlan:
    activity: object # TODO: Activity Schema
    restaurant: object # TODO: Restauraunt Schema

@dataclass
class OutingConstraints:
    id: str
    visitor_id: str
    start_time: datetime
    search_area_ids: list[str]
    budget: int
    headcount: int

@dataclass
class EventbriteCategory:
    id: str
    subcategory_id: str

@dataclass
class UserPreferences:
    open_to_bars: bool
    requires_wheelchair_accessibility: bool
    google_food_types: list[str]
    eventbrite_categories: list[EventbriteCategory]

@dataclass
class User:
    id: str | None
    visitor_id: str | None
    preferences: UserPreferences
