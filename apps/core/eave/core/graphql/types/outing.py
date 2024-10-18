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


@strawberry.enum
class SurveySubmitErrorCode(enum.StrEnum):
    START_TIME_TOO_SOON = "START_TIME_TOO_SOON"
    START_TIME_TOO_LATE = "START_TIME_TOO_LATE"


@strawberry.type
class SurveySubmitSuccess:
    outing: Outing


@strawberry.type
class SurveySubmitError:
    error_code: SurveySubmitErrorCode


SurveySubmitResult = Annotated[SurveySubmitSuccess | SurveySubmitError, strawberry.union("SurveySubmitResult")]


@strawberry.enum
class ReplanOutingErrorCode(enum.StrEnum):
    START_TIME_PASSED = "START_TIME_PASSED"


@strawberry.type
class ReplanOutingSuccess:
    outing: Outing


@strawberry.type
class ReplanOutingError:
    error_code: ReplanOutingErrorCode


ReplanOutingResult = Annotated[ReplanOutingSuccess | ReplanOutingError, strawberry.union("ReplanOutingResult")]
