import enum
from datetime import datetime
from uuid import UUID

import strawberry

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
    survey_id: UUID
    budget: OutingBudget
    headcount: int
    activity: Activity | None
    activity_start_time: datetime | None
    restaurant: Restaurant | None
    restaurant_arrival_time: datetime | None
    driving_time: str

    # @classmethod
    # def from_orm(cls, orm: OutingOrm) -> "Outing":
    #     return Outing(
    #         id=orm.id,
    #         survey_id=orm.survey_id,
    #         budget=orm.budget,
    #         headcount=orm.headcount,
    #         visitor_id=orm.visitor_id,
    #     )


@strawberry.type
class ProposedOuting:
    activity: Activity | None
    activity_start_time: datetime | None
    restaurant: Restaurant | None
    restaurant_arrival_time: datetime | None
    driving_time: str | None
