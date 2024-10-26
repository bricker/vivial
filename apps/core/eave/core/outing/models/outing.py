from dataclasses import dataclass
from datetime import datetime

from eave.stdlib.eventbrite.models.event import Event
from eave.stdlib.google.places.models.place import Place

@dataclass
class OutingConstraints:
    start_time: datetime
    search_area_ids: list[str]
    budget: int
    headcount: int

@dataclass
class OutingPlan:
    activity: Event | Place | None
    restaurant: Place | None
