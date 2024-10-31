from dataclasses import dataclass
from datetime import datetime

from google.maps.places_v1.types import Place

from eave.stdlib.eventbrite.models.event import Event

from .geo_area import GeoLocation
from .sources import EventSource


class OutingComponent:
    source: EventSource
    event: Event | None
    place: Place | None
    location: GeoLocation
    start_time: datetime

    def __init__(
        self,
        source: EventSource,
        location: GeoLocation,
        start_time: datetime,
        event: Event | None = None,
        place: Place | None = None,
    ) -> None:
        self.source = source
        self.location = location
        self.event = event
        self.place = place
        self.start_time = start_time


@dataclass
class OutingPlan:
    activity: OutingComponent | None
    restaurant: OutingComponent | None
