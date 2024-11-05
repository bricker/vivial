import enum
from typing import Annotated
from uuid import UUID

import strawberry


@strawberry.type
class Outing:
    id: UUID
    visitor_id: UUID
    account_id: UUID | None
    survey_id: UUID


@strawberry.input
class ReplanOutingInput:
    visitor_id: UUID
    outing_id: UUID


@strawberry.enum
class SubmitSurveyErrorCode(enum.StrEnum):
    START_TIME_TOO_SOON = "START_TIME_TOO_SOON"
    START_TIME_TOO_LATE = "START_TIME_TOO_LATE"
    ONE_SEARCH_REGION_REQUIRED = "ONE_SEARCH_REGION_REQUIRED"


@strawberry.type
class SubmitSurveySuccess:
    outing: Outing


@strawberry.type
class SubmitSurveyError:
    error_code: SubmitSurveyErrorCode


SubmitSurveyResult = Annotated[SubmitSurveySuccess | SubmitSurveyError, strawberry.union("SubmitSurveyResult")]


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
