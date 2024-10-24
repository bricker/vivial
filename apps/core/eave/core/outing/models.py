from dataclasses import dataclass
from datetime import datetime

@dataclass
class OutingPlan:
    activity: object # TODO: Activity Schema
    restaurant: object # TODO: Restauraunt Schema








@dataclass
class OutingRestaurant:
    name: str




@dataclass
class OutingConstraints:
    start_time: datetime
    search_area_ids: list[str]
    budget: int
    headcount: int




@dataclass
class TimeInterval:
    start: datetime
    end: datetime


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




@dataclass
class TimeOfDay:
    day: int
    hour: int
    minute: int

@dataclass
class OperatingPeriod:
    open: TimeOfDay
    close: TimeOfDay


@dataclass
class OperatingHours:
    monday: list[OperatingPeriod]
    tuesday: list[OperatingPeriod]
    wednesday: list[OperatingPeriod]
    thursday: list[OperatingPeriod]
    friday: list[OperatingPeriod]
    saturday: list[OperatingPeriod]
    sunday: list[OperatingPeriod]


@dataclass
class Location:
    name: str
    address_1: str
    address_2: str
    city: str
    region: str
    postal_code: str
    country: str
    lat: float
    lon: float
    operating_hours: OperatingHours | None


@dataclass
class Image:
    url: str
    alt_text: str

@dataclass
class Activity:
    id: str
    name: str
    description: str
    url: str
    cover_image: Image | None
    images: list[Image] | None
    location: Location
    min_ticket_price: int
    max_ticket_price: int




@dataclass
class Restaurant:
    id: str

