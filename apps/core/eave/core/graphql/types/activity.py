from uuid import UUID

import strawberry

from eave.core.graphql.types.pricing import Pricing
from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.activity_category_group import ActivityCategoryGroupOrm
from eave.core.shared.enums import ActivitySource

from .location import Location
from .photos import Photos


@strawberry.type
class ActivityVenue:
    name: str
    location: Location


@strawberry.type
class Activity:
    source_id: str
    source: ActivitySource
    name: str
    description: str
    venue: ActivityVenue
    photos: Photos | None
    pricing: Pricing | None
    website_uri: str | None
    door_tips: str | None
    insider_tips: str | None
    parking_tips: str | None


@strawberry.type
class ActivityCategory:
    id: UUID
    name: str
    is_default: bool

    @classmethod
    def from_orm(cls, orm: ActivityCategoryOrm) -> "ActivityCategory":
        return ActivityCategory(
            id=orm.id,
            name=orm.name,
            is_default=orm.is_default,
        )


@strawberry.type
class ActivityCategoryGroup:
    id: UUID
    name: str
    activity_categories: list[ActivityCategory]

    @classmethod
    def from_orm(cls, orm: ActivityCategoryGroupOrm) -> "ActivityCategoryGroup":
        return ActivityCategoryGroup(
            id=orm.id,
            name=orm.name,
            activity_categories=[ActivityCategory.from_orm(orm) for orm in orm.activity_categories],
        )
