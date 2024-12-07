from datetime import datetime
from uuid import UUID

import strawberry

from .activity import Activity
from .restaurant import Restaurant


@strawberry.type
class Outing:
    id: UUID
    headcount: int
    activity: Activity | None
    activity_start_time: datetime | None
    restaurant: Restaurant | None
    restaurant_arrival_time: datetime | None
    driving_time: str | None


@strawberry.type
class ProposedOuting:
    activity: Activity | None
    activity_start_time: datetime | None
    restaurant: Restaurant | None
    restaurant_arrival_time: datetime | None
    driving_time: str | None
