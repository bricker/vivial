import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.account import Account
from eave.core.graphql.types.viewer import Viewer
from eave.core.orm.account import AccountOrm
from eave.stdlib.util import unwrap


async def viewer_query(*, info: strawberry.Info[GraphQLContext]) -> Viewer:
    return Viewer()
