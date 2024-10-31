from dataclasses import dataclass
from datetime import datetime

from eave.stdlib.eventbrite.models.event import Event
from eave.stdlib.google.places.models.place import Place

from .geo_area import GeoLocation
from .search_region_code import SearchRegionCode
from .sources import EventSource


@dataclass
class OutingComponent:
    source: EventSource
    external_details: Event | Place
    location: GeoLocation
    start_time: datetime


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
