from typing import Annotated
from uuid import UUID

import strawberry


@strawberry.type
class Outing:
    id: UUID
    visitor_id: str
    account_id: UUID | None
    survey_id: UUID
    # TODO: rest of the fields from ORM once that's finished


@strawberry.type
class SurveySubmitSuccess:
    outing: Outing


@strawberry.type
class SurveySubmitError:
    pass


SurveySubmitResult = Annotated[SurveySubmitSuccess | SurveySubmitError, strawberry.union("SurveySubmitResult")]


@strawberry.type
class ReplanOutingSuccess:
    outing: Outing


@strawberry.type
class ReplanOutingError:
    pass


ReplanOutingResult = Annotated[ReplanOutingSuccess | ReplanOutingError, strawberry.union("ReplanOutingResult")]
