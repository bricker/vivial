import strawberry

from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.viewer import Viewer


async def viewer_query(*, info: strawberry.Info[GraphQLContext]) -> Viewer:
    return Viewer()
