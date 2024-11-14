import enum
from datetime import datetime
from uuid import UUID

import strawberry
from google.maps.places_v1 import PriceLevel

from eave.core.shared.enums import OutingBudget

from .activity import Activity
from .restaurant import Restaurant


@strawberry.enum
class OutingState(enum.StrEnum):
    PAST = enum.auto()
    FUTURE = enum.auto()


@strawberry.type
class Outing:
    id: UUID
    visitor_id: UUID
    account_id: UUID | None
    survey_id: UUID
    budget: OutingBudget
    headcount: int
    activity: Activity | None
    activity_start_time: datetime | None
    restaurant: Restaurant | None
    restaurant_arrival_time: datetime | None
    driving_time: str

@strawberry.type
class ProposedOuting:
    activity: Activity | None
    activity_start_time: datetime | None
    restaurant: Restaurant | None
    restaurant_arrival_time: datetime | None
    driving_time: str | None
