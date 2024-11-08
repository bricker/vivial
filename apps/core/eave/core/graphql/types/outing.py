import enum
from datetime import datetime
from typing import Annotated
from uuid import UUID

import strawberry

from .activity import Activity
from .restaurant import Restaurant


@strawberry.enum
class OutingState(enum.StrEnum):
    PAST = "PAST"
    FUTURE = "FUTURE"


@strawberry.enum
class OutingBudget(enum.IntEnum):
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


@strawberry.enum
class SubmitSurveyErrorCode(enum.StrEnum):
    START_TIME_TOO_SOON = "START_TIME_TOO_SOON"
    START_TIME_TOO_LATE = "START_TIME_TOO_LATE"
    ONE_SEARCH_REGION_REQUIRED = "ONE_SEARCH_REGION_REQUIRED"


@strawberry.type
class PlanOutingSuccess:
    outing: Outing


@strawberry.type
class SubmitSurveyError:
    error_code: SubmitSurveyErrorCode


SubmitSurveyResult = Annotated[PlanOutingSuccess | SubmitSurveyError, strawberry.union("SubmitSurveyResult")]


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
