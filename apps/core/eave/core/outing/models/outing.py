from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from models.search_region_code import SearchRegionCode

from eave.stdlib.eventbrite.models.event import Event
from eave.stdlib.google.places.models.place import Place


class ActivitySource(StrEnum):
    INTERNAL = "INTERNAL"
    EVENTBRITE = "EVENTBRITE"


class RestaurantSource(StrEnum):
    GOOGLE = "GOOGLE"


@dataclass
class OutingComponent:
    source: ActivitySource | RestaurantSource
    details: Event | Place | None


@dataclass
class OutingPlan:
    activity: OutingComponent | None
    restaurant: OutingComponent | None


@dataclass
class OutingConstraints:
    start_time: datetime
    search_area_ids: list[SearchRegionCode]
    budget: int
    headcount: int
