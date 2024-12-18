from datetime import datetime
from uuid import UUID

import strawberry

from eave.core.graphql.types.activity import ActivityPlan
from eave.core.graphql.types.cost_breakdown import CostBreakdown
from eave.core.graphql.types.reserver_details import ReserverDetails
from eave.core.graphql.types.restaurant import Reservation
from eave.core.graphql.types.search_region import SearchRegion
from eave.core.orm.booking import BookingOrm
from eave.core.shared.enums import BookingState, OutingBudget


@strawberry.type
class Booking:
    id: UUID
    reserver_details: ReserverDetails | None
    state: BookingState

    @classmethod
    def from_orm(cls, orm: BookingOrm) -> "Booking":
        return Booking(
            id=orm.id,
            reserver_details=ReserverDetails.from_orm(orm.reserver_details) if orm.reserver_details else None,
            state=orm.state,
        )


@strawberry.type
class BookingDetailPeek:
    id: UUID
    activity_start_time: datetime | None
    activity_name: str | None
    restaurant_arrival_time: datetime | None
    restaurant_name: str | None
    photo_uri: str | None
    state: BookingState


@strawberry.type
class BookingDetails:
    id: UUID
    state: BookingState
    activity_plan: ActivityPlan | None
    reservation: Reservation | None

    @strawberry.field
    def search_regions(self) -> list[SearchRegion]:
        search_regions: list[SearchRegion] = []

        if self.activity_plan:
            search_regions.append(self.activity_plan.activity.venue.location.find_closest_search_region())

        if self.reservation:
            search_regions.append(self.reservation.restaurant.location.find_closest_search_region())

        return search_regions


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
        return 15  # FIXME: ABL

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
