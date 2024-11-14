from datetime import datetime
from uuid import UUID

import strawberry

from eave.core.shared.enums import OutingBudget


@strawberry.type
class Survey:
    id: UUID
    visitor_id: UUID
    start_time: datetime
    search_area_ids: list[UUID]
    budget: OutingBudget
    headcount: int


@strawberry.input
class SurveyInput:
    visitor_id: UUID
    start_time: datetime
    search_area_ids: list[UUID]
    budget: OutingBudget
    headcount: int
