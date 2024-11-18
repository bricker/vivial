from datetime import datetime
from uuid import UUID

import strawberry

from eave.core.orm.survey import SurveyOrm
from eave.core.shared.enums import OutingBudget


@strawberry.type
class Survey:
    id: UUID
    visitor_id: UUID
    start_time: datetime
    search_area_ids: list[UUID]
    budget: OutingBudget
    headcount: int

    @classmethod
    def from_orm(cls, orm: SurveyOrm) -> "Survey":
        return Survey(
            id=orm.id,
            visitor_id=orm.visitor_id,
            start_time=orm.start_time,
            search_area_ids=orm.search_area_ids,
            budget=orm.outing_budget,
            headcount=orm.headcount,
        )


@strawberry.input
class SurveyInput:
    visitor_id: UUID
    start_time: datetime
    search_area_ids: list[UUID]
    budget: OutingBudget
    headcount: int
