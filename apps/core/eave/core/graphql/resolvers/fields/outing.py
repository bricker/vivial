from datetime import UTC, datetime, timedelta
from uuid import UUID

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.activity import Activity
from eave.core.graphql.types.outing import (
    Outing,
)
from eave.core.graphql.types.pricing import CostBreakdown
from eave.core.graphql.types.restaurant import Restaurant
from eave.core.graphql.types.search_region import SearchRegion
from eave.core.graphql.types.survey import Survey
from eave.core.lib.event_helpers import get_activity, get_restaurant
from eave.core.orm.outing import OutingOrm
from eave.core.orm.search_region import SearchRegionOrm


@strawberry.input
class OutingInput:
    id: UUID


async def get_outing_query(*, info: strawberry.Info[GraphQLContext], input: OutingInput) -> Outing | None:
    async with database.async_session.begin() as db_session:
        outing = await OutingOrm.get_one(db_session, input.id)

    activity: Activity | None = None
    restaurant: Restaurant | None = None
    headcount = 0
    activity_start_time: datetime | None = None
    restaurant_arrival_time: datetime | None = None
    cost_breakdown = CostBreakdown()

    if len(outing.activities) > 0:
        # Currently the client only supports 1 activity per outing.
        outing_activity_orm = outing.activities[0]
        # This is a quick way to expire an outing URL 24 hours before the outing beings.
        if outing_activity_orm.start_time_utc < (datetime.now(UTC) + timedelta(hours=24)):
            return None

        headcount = max(headcount, outing_activity_orm.headcount)
        activity_start_time = outing_activity_orm.start_time_local

        activity = await get_activity(
            source=outing_activity_orm.source,
            source_id=outing_activity_orm.source_id,
        )

        if activity:
            if activity.ticket_info:
                cost_breakdown = activity.ticket_info.cost_breakdown * outing_activity_orm.headcount

    if len(outing.reservations) > 0:
        # Currently the client only supports 1 restaurant per outing.
        outing_reservation_orm = outing.reservations[0]
        headcount = max(headcount, outing_reservation_orm.headcount)
        restaurant_arrival_time = outing_reservation_orm.start_time_local

        restaurant = await get_restaurant(
            source=outing_reservation_orm.source,
            source_id=outing_reservation_orm.source_id,
        )

    return Outing(
        id=outing.id,
        survey=Survey.from_orm(outing.survey),
        cost_breakdown=cost_breakdown,
        activity=activity,
        restaurant=restaurant,
        driving_time=None,
        activity_start_time=activity_start_time,
        restaurant_arrival_time=restaurant_arrival_time,
    )
