from datetime import datetime
from uuid import UUID

import strawberry

from eave.core.graphql.types.cost_breakdown import CostBreakdown
from eave.core.graphql.types.survey import Survey

from .activity import Activity, ActivityPlan
from .restaurant import Reservation, Restaurant


@strawberry.input
class OutingPreferencesInput:
    restaurant_category_ids: list[UUID]
    activity_category_ids: list[UUID]


@strawberry.type
class Outing:
    id: UUID
    survey: Survey | None
    activity_plan: ActivityPlan | None
    reservation: Reservation | None

    @strawberry.field
    async def driving_time_minutes(self) -> int | None:
        return 15 # FIXME: ABL

    @strawberry.field
    def cost_breakdown(self) -> CostBreakdown:
        return self.calculate_cost_breakdown()

    def calculate_cost_breakdown(self) -> CostBreakdown:
        cb = CostBreakdown()

        if self.activity_plan:
            cb += self.activity_plan.calculate_cost_breakdown()

        if self.reservation:
            cb += self.reservation.calculate_cost_breakdown()

        return cb
