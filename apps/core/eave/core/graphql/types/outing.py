from datetime import datetime
from uuid import UUID

import strawberry

from eave.core.graphql.types.pricing import CostBreakdown
from eave.core.graphql.types.search_region import SearchRegion
from eave.core.graphql.types.survey import Survey

from .activity import Activity
from .restaurant import Restaurant


@strawberry.input
class OutingPreferencesInput:
    restaurant_category_ids: list[UUID]
    activity_category_ids: list[UUID]


@strawberry.type
class Outing:
    id: UUID
    cost_breakdown: CostBreakdown
    headcount: int
    survey: Survey
    activity: Activity | None
    activity_start_time: datetime | None
    activity_region: SearchRegion | None
    restaurant: Restaurant | None
    restaurant_arrival_time: datetime | None
    restaurant_region: SearchRegion | None
    driving_time: str | None
