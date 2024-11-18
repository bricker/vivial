from uuid import UUID

import strawberry

from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.activity_subcategory import ActivitySubcategoryOrm
from eave.core.shared.enums import ActivitySource

from .location import Location
from .photos import Photos


@strawberry.type
class ActivityTicketInfo:
    type: str | None
    notes: str | None
    cost: int | None = 0
    fee: int | None = 0
    tax: int | None = 0


@strawberry.type
class ActivityVenue:
    name: str
    location: Location


@strawberry.type
class Activity:
    id: str
    source: ActivitySource
    name: str
    description: str
    venue: ActivityVenue
    photos: Photos | None
    ticket_info: ActivityTicketInfo | None
    website_uri: str | None
    door_tips: str | None
    insider_tips: str | None
    parking_tips: str | None


@strawberry.type
class ActivitySubcategory:
    id: UUID
    name: str
    is_default: bool

    @classmethod
    def from_orm(cls, orm: ActivitySubcategoryOrm) -> "ActivitySubcategory":
        return ActivitySubcategory(
            id=orm.id,
            name=orm.name,
            is_default=orm.is_default,
        )


@strawberry.type
class ActivityCategory:
    id: UUID
    name: str
    subcategories: list[ActivitySubcategory]

    @classmethod
    def from_orm(cls, orm: ActivityCategoryOrm) -> "ActivityCategory":
        return ActivityCategory(
            id=orm.id,
            name=orm.name,
            subcategories=[ActivitySubcategory.from_orm(orm) for orm in orm.subcategories],
        )
