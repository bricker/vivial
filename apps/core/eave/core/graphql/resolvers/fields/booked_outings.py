
import strawberry

from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.resolvers.fields.outing import MOCK_OUTING
from eave.core.graphql.types.outing import (
    Outing,
    OutingState,
)


async def list_booked_outings_query(
    *, info: strawberry.Info[GraphQLContext], outing_state: OutingState
) -> list[Outing]:
    # TODO: Fetch list of booked outings by account ID.
    # PAST outings are outings that have already occured.
    # FUTURE outings are upcoming outings.
    return [MOCK_OUTING, MOCK_OUTING]
