from dataclasses import dataclass
from datetime import datetime

from google.maps.places_v1.types import Place

from eave.stdlib.eventbrite.models.event import Event

from .geo_area import GeoLocation
from ...graphql.types.search_region_code import SearchRegionCode
from .sources import ActivitySource, RestaurantSource


class OutingComponent:
    source: ActivitySource | RestaurantSource
    event: Event | None
    place: Place | None
    location: GeoLocation

    def __init__(
        self,
        source: ActivitySource | RestaurantSource,
        location: GeoLocation,
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
