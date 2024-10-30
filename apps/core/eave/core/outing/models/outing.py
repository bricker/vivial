from dataclasses import dataclass
from datetime import datetime

from models.geo_area import GeoLocation
from models.search_region_code import SearchRegionCode
from models.sources import ActivitySource, RestaurantSource

from eave.stdlib.eventbrite.models.event import Event
from eave.stdlib.google.places.models.place import Place


@dataclass
class OutingComponent:
    source: ActivitySource | RestaurantSource
    external_details: Event | Place
    location: GeoLocation


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
