import enum
from datetime import datetime
from uuid import UUID

import strawberry

from eave.core.orm.outing import OutingOrm
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
    headcount: int
    activity: Activity | None
    activity_start_time: datetime | None
    restaurant: Restaurant | None
    restaurant_arrival_time: datetime | None
    driving_time: str

    @classmethod
    def from_orm(cls, orm: OutingOrm) -> "Outing":
        pass
        # return Outing(
        #     id=orm.id,
        #     headcount=orm.headcount,
        #     activity=,
        #     activity_start_time=,
        #     restaurant=,
        #     restaurant_arrival_time=,
        #     driving_time=,
        # )


@strawberry.type
class ProposedOuting:
    activity: Activity | None
    activity_start_time: datetime | None
    restaurant: Restaurant | None
    restaurant_arrival_time: datetime | None
    driving_time: str | None
