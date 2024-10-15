from eave.core.graphql.resolvers.survey import submit_survey_for_plan_mutation
import strawberry

from eave.core.graphql.resolvers.authentication import (
    login_mutation,
    logout_mutation,
    refresh_tokens_mutation,
    register_mutation,
)


@strawberry.type
class Mutation:
    register = strawberry.mutation(resolver=register_mutation)
    login = strawberry.mutation(resolver=login_mutation)
    refresh_tokens = strawberry.mutation(resolver=refresh_tokens_mutation)
    logout = strawberry.mutation(resolver=logout_mutation)
    submit_survey_for_plan = strawberry.mutation(resolver=submit_survey_for_plan_mutation)
