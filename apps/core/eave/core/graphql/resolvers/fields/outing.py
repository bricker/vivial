from datetime import UTC, datetime, timedelta
from uuid import UUID

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.activity import ActivityPlan
from eave.core.graphql.types.outing import (
    Outing,
)
from eave.core.graphql.types.restaurant import Reservation
from eave.core.graphql.types.survey import Survey
from eave.core.lib.event_helpers import resolve_activity_details, resolve_restaurant_details
from eave.core.orm.outing import OutingOrm


@strawberry.input
class OutingInput:
    id: UUID


async def get_outing_query(*, info: strawberry.Info[GraphQLContext], input: OutingInput) -> Outing | None:
    async with database.async_session.begin() as db_session:
        outing_orm = await OutingOrm.get_one(db_session, input.id)

    one_day_from_now = datetime.now(UTC) + timedelta(hours=24)

    activity_plan: ActivityPlan | None = None
    reservation: Reservation | None = None

    if len(outing_orm.activities) > 0:
        # Currently the client only supports 1 activity per outing.
        outing_activity_orm = outing_orm.activities[0]

        # This is a quick way to expire an outing URL 24 hours before the outing beings.
        if outing_activity_orm.start_time_utc < one_day_from_now:
            return None

        activity = await resolve_activity_details(
            source=outing_activity_orm.source,
            source_id=outing_activity_orm.source_id,
            survey=outing_orm.survey,
        )

        if activity:
            activity_plan = ActivityPlan(
                activity=activity,
                headcount=outing_activity_orm.headcount,
                start_time=outing_activity_orm.start_time_local,
            )

    if len(outing_orm.reservations) > 0:
        # Currently the client only supports 1 restaurant per outing.
        outing_reservation_orm = outing_orm.reservations[0]

        # This is a quick way to expire an outing URL 24 hours before the outing beings.
        if outing_reservation_orm.start_time_utc < one_day_from_now:
            return None

        restaurant = await resolve_restaurant_details(
            source=outing_reservation_orm.source,
            source_id=outing_reservation_orm.source_id,
        )

        reservation = Reservation(
            restaurant=restaurant,
            arrival_time=outing_reservation_orm.start_time_local,
            headcount=outing_reservation_orm.headcount,
        )

    return Outing(
        id=outing_orm.id,
        survey=Survey.from_orm(outing_orm.survey) if outing_orm.survey else None,
        activity_plan=activity_plan,
        reservation=reservation,
    )
