from dataclasses import dataclass
from datetime import datetime

from eave.stdlib.eventbrite.models.event import Event
from eave.stdlib.google.places.models.place import Place
from shapely import Point

from .search_region_code import SearchRegionCode
from .sources import ActivitySource, RestaurantSource


@dataclass
class OutingComponent:
    source: ActivitySource | RestaurantSource
    external_details: Event | Place
    location: Point


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
