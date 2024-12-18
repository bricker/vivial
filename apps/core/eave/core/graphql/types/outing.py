import random
from datetime import datetime
from uuid import UUID

import strawberry

from eave.core.graphql.types.cost_breakdown import CostBreakdown
from eave.core.graphql.types.search_region import SearchRegion
from eave.core.graphql.types.survey import Survey

from .activity import ActivityPlan
from .restaurant import Reservation


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
    def search_regions(self) -> list[SearchRegion]:
        search_regions: dict[UUID, SearchRegion] = {}

        if self.activity_plan:
            r = self.activity_plan.activity.venue.location.find_closest_search_region()
            search_regions[r.id] = r

        if self.reservation:
            r = self.reservation.restaurant.location.find_closest_search_region()
            search_regions[r.id] = r

        return list(search_regions.values())

    @strawberry.field
    def headcount(self) -> int:
        headcount = 0

        if self.reservation:
            headcount = max(headcount, self.reservation.headcount)

        if self.activity_plan:
            headcount = max(headcount, self.activity_plan.headcount)

        if headcount == 0:
            raise ValueError("invalid headcount 0")

        return headcount

    @strawberry.field
    def start_time(self) -> datetime:
        if self.reservation:
            return self.reservation.arrival_time
        elif self.activity_plan:
            return self.activity_plan.start_time
        else:
            raise ValueError("both reservation and activity_plan are None")

    @strawberry.field
    async def driving_time_minutes(self) -> int | None:
        return random.choice(range(5, 15))  # FIXME: ABL  # noqa: S311

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
