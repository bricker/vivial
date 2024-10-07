import strawberry

from eave.core.graphql.types.account import AuthenticatedUser

@strawberry.type
class Query:
    viewer: AuthenticatedUser = strawberry.field(resolver=x)
