import enum
from datetime import datetime
from typing import Annotated
from uuid import UUID

import strawberry

from eave.core.graphql.types.search_region import SearchRegionCode
from eave.core.graphql.types.user import UserInput

from .activity import Activity
from .restaurant import Restaurant


@strawberry.enum
class OutingBudget(enum.IntEnum):
    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4


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


@strawberry.input
class ReplanOutingInput:
    visitor_id: UUID
    outing_id: UUID


@strawberry.input
class PlanOutingInput:
    visitor_id: UUID
    group: list[UserInput]
    start_time: datetime
    search_area_ids: list[SearchRegionCode]
    budget: OutingBudget
    headcount: int


@strawberry.enum
class PlanOutingErrorCode(enum.StrEnum):
    START_TIME_TOO_SOON = "START_TIME_TOO_SOON"
    START_TIME_TOO_LATE = "START_TIME_TOO_LATE"
    ONE_SEARCH_REGION_REQUIRED = "ONE_SEARCH_REGION_REQUIRED"


@strawberry.type
class PlanOutingSuccess:
    outing: Outing


@strawberry.type
class PlanOutingError:
    error_code: PlanOutingErrorCode


PlanOutingResult = Annotated[PlanOutingSuccess | PlanOutingError, strawberry.union("PlanOutingResult")]


@strawberry.enum
class ReplanOutingErrorCode(enum.StrEnum):
    START_TIME_TOO_SOON = "START_TIME_TOO_SOON"
    START_TIME_TOO_LATE = "START_TIME_TOO_LATE"


@strawberry.type
class ReplanOutingSuccess:
    outing: Outing


@strawberry.type
class ReplanOutingError:
    error_code: ReplanOutingErrorCode


ReplanOutingResult = Annotated[ReplanOutingSuccess | ReplanOutingError, strawberry.union("ReplanOutingResult")]
