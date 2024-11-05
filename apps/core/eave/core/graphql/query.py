import strawberry

from eave.core.graphql.resolvers.viewer import viewer_query
from eave.core.graphql.types.authentication import Account





@strawberry.type
class Dummy:
    doggo: str


async def dummy_query() -> Dummy:
    return Dummy(
        doggo="Suzanne"
    )


@strawberry.type
class Query:
    viewer: Account = strawberry.field(resolver=viewer_query)
    dummy: Dummy = strawberry.field(resolver=dummy_query)
