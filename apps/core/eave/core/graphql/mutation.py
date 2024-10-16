import strawberry

from eave.core.graphql.resolvers.authentication import (
    login_mutation,
    logout_mutation,
    refresh_tokens_mutation,
    register_mutation,
)
from eave.core.graphql.resolvers.outing import outing_from_survey_mutation, replan_outing_mutation


@strawberry.type
class Mutation:
    register = strawberry.mutation(resolver=register_mutation)
    login = strawberry.mutation(resolver=login_mutation)
    refresh_tokens = strawberry.mutation(resolver=refresh_tokens_mutation)
    logout = strawberry.mutation(resolver=logout_mutation)
    outing_from_survey = strawberry.mutation(resolver=outing_from_survey_mutation)
    replan_outing = strawberry.mutation(resolver=replan_outing_mutation)
