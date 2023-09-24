import strawberry

from eave.core.graphql.types.team import Team

@strawberry.type
class Query:
    @strawberry.field
    def teams(self) -> list[Team]:
        return []
