from dataclasses import dataclass
from datetime import datetime

from google.maps.places_v1.types import Place

from eave.core.lib.geo import GeoPoint
from eave.stdlib.eventbrite.models.event import Event

from .search_region import SearchRegionCode
from .sources import ActivitySource, RestaurantSource


class OutingComponent:
    source: ActivitySource | RestaurantSource
    event: Event | None
    place: Place | None
    location: GeoPoint

    def __init__(
        self,
        source: ActivitySource | RestaurantSource,
        location: GeoPoint,
        event: Event | None = None,
        place: Place | None = None,
    ) -> None:
        self.source = source
        self.location = location
        self.event = event
        self.place = place


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
