from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from google.maps.places_v1.types import Place

from eave.core.graphql.types.activity import EventSource
from eave.core.graphql.types.outing import OutingBudget
from eave.core.graphql.types.restaurant import EventSource
from eave.core.lib.geo import GeoPoint
from eave.stdlib.eventbrite.models.event import Event


class OutingComponent:
    source: EventSource | EventSource
    event: Event | None
    place: Place | None
    location: GeoPoint

    def __init__(
        self,
        source: EventSource | EventSource,
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
    search_area_ids: list[UUID]
    budget: OutingBudget
    headcount: int
