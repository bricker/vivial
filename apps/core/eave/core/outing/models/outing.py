from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from google.maps.places_v1.types import Place

from eave.core.graphql.types.event_source import EventSource
from eave.core.graphql.types.outing import OutingBudget
from eave.core.lib.geo import GeoPoint
from eave.stdlib.eventbrite.models.event import Event


class OutingComponent:
    source: EventSource
    event: Event | None
    place: Place | None
    location: GeoPoint
    start_time: datetime

    def __init__(
        self,
        source: EventSource,
        location: GeoPoint,
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
