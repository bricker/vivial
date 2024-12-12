from datetime import datetime
from uuid import UUID

import strawberry

from eave.core.shared.enums import OutingBudget

from .activity import Activity
from .restaurant import Restaurant


@strawberry.input
class OutingPreferencesInput:
    restaurant_category_ids: list[UUID]
    activity_category_ids: list[UUID]


@strawberry.type
class Outing:
    id: UUID
    headcount: int
    budget: OutingBudget
    activity: Activity | None
    activity_start_time: datetime | None
    restaurant: Restaurant | None
    restaurant_arrival_time: datetime | None
    driving_time: str | None
