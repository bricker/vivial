from datetime import datetime
from typing import Annotated
from uuid import UUID

import strawberry


@strawberry.type
class Survey:
    id: UUID
    visitor_id: str
    start_time: datetime
    search_area_ids: list[str]
    budget: int
    headcount: int


@strawberry.type
class SurveySubmitSuccess:
    pass


@strawberry.type
class SurveySubmitError:
    pass


SurveySubmitResult = Annotated[SurveySubmitSuccess | SurveySubmitError, strawberry.union("SurveySubmitResult")]
