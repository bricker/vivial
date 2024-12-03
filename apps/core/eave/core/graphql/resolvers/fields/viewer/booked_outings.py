import copy
import datetime

import strawberry

from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.resolvers.fields.outing import MOCK_OUTING
from eave.core.graphql.types.outing import (
    Outing,
    OutingState,
)


@strawberry.input
class ListBookedOutingsInput:
    outing_state: OutingState


async def list_booked_outings_query(
    *,
    info: strawberry.Info[GraphQLContext],
    input: ListBookedOutingsInput | None = None,
) -> list[Outing]:
    # TODO: Fetch list of booked outings by account ID.
    # PAST outings are outings that have already occured.
    # FUTURE outings are upcoming outings.
    fut = copy.deepcopy(MOCK_OUTING)
    fut.activity_start_time = datetime.datetime.now() + datetime.timedelta(hours=1)
    fut.restaurant_arrival_time = datetime.datetime.now() + datetime.timedelta(hours=1)
    return [MOCK_OUTING, fut]
