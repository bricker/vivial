import enum
from datetime import datetime
from uuid import UUID

import strawberry

from eave.core.orm.outing import OutingOrm

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
    driving_time: str | None

    @classmethod
    def from_orm(cls, orm: OutingOrm) -> "Outing":
        # FIXME: delete this garbo
        return Outing(
            id=orm.id,
            headcount=2,
            activity=None,
            activity_start_time=None,
            restaurant=None,
            restaurant_arrival_time=None,
            driving_time=None,
        )


@strawberry.type
class ProposedOuting:
    activity: Activity | None
    activity_start_time: datetime | None
    restaurant: Restaurant | None
    restaurant_arrival_time: datetime | None
    driving_time: str | None
