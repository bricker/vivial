from enum import StrEnum
from dataclasses import dataclass
from datetime import datetime

from eave.stdlib.eventbrite.models.event import Event
from eave.stdlib.google.places.models.place import Place


class OutingSource(StrEnum):
    INTERNAL = "INTERNAL"
    GOOGLE = "GOOGLE"
    EVENTBRITE = "EVENTBRITE"

@dataclass
class OutingComponent:
    source: OutingSource
    details: Event | Place | None

@dataclass
class OutingPlan:
    activity: OutingComponent | None
    restaurant: OutingComponent | None

@dataclass
class OutingConstraints:
    start_time: datetime
    search_area_ids: list[str]
    budget: int
    headcount: int
