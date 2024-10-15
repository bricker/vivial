import strawberry

from eave.core.graphql.resolvers.viewer import viewer_query
from eave.core.graphql.types.authentication import Account


@strawberry.type
class Query:
    viewer: Account = strawberry.field(resolver=viewer_query)
