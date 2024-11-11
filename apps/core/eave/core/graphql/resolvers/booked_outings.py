from datetime import datetime
from uuid import UUID, uuid4

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.resolvers.outing import MOCK_OUTING
from eave.core.graphql.types.activity import Activity, ActivityTicketInfo, ActivityVenue
from eave.core.graphql.types.location import Location
from eave.core.graphql.types.outing import (
    Outing,
    OutingBudget,
    OutingState,
)
from eave.core.graphql.types.photos import Photos
from eave.core.graphql.types.restaurant import Restaurant
from eave.core.lib.analytics import ANALYTICS
from eave.core.orm.outing import OutingOrm
from eave.core.orm.outing_activity import OutingActivityOrm
from eave.core.orm.outing_reservation import OutingReservationOrm
from eave.core.zoneinfo import LOS_ANGELES_ZONE_INFO

async def list_booked_outings_query(*, info: strawberry.Info[GraphQLContext], outing_state: OutingState) -> list[Outing]:
    # TODO: Fetch list of booked outings by account ID.
    # PAST outings are outings that have already occured.
    # FUTURE outings are upcoming outings.
    return [MOCK_OUTING, MOCK_OUTING]
