from datetime import datetime
from uuid import UUID

import strawberry

from eave.core.graphql.types.cost_breakdown import CostBreakdown
from eave.core.graphql.types.ticket_info import TicketInfo
from eave.core.lib.address import format_address
from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.activity_category_group import ActivityCategoryGroupOrm
from eave.core.shared.enums import ActivitySource
from eave.stdlib.typing import JsonObject

from .location import Location
from .photos import Photos


@strawberry.type
class ActivityVenue:
    name: str
    location: Location


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


@strawberry.type
class Activity:
    source_id: str
    source: ActivitySource
    name: str
    description: str | None
    venue: ActivityVenue
    photos: Photos
    ticket_info: TicketInfo | None
    website_uri: str | None
    door_tips: str | None
    insider_tips: str | None
    parking_tips: str | None
    primary_type_name: str | None
    category_group: ActivityCategoryGroup | None
    is_bookable: bool


@strawberry.type
class ActivityPlan:
    start_time: datetime
    headcount: int
    activity: Activity

    @strawberry.field
    def cost_breakdown(self) -> CostBreakdown:
        return self.calculate_cost_breakdown()

    def calculate_cost_breakdown(self) -> CostBreakdown:
        cb = self.activity.ticket_info.cost_breakdown if self.activity.ticket_info else CostBreakdown()
        return cb * self.headcount

    def build_analytics_properties(self) -> JsonObject:
        return {
            "start_time": self.start_time.isoformat(),
            "category": self.activity.category_group.name if self.activity.category_group else None,
            "costs": self.calculate_cost_breakdown().build_analytics_properties(),
            "address": format_address(self.activity.venue.location.address.to_address(), singleline=True),
        }
