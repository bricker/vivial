import strawberry

from eave.core.graphql.resolvers.authentication import (
    login_mutation,
    logout_mutation,
    refresh_tokens_mutation,
    register_mutation,
)
from eave.core.graphql.resolvers.booking import create_booking_mutation
from eave.core.graphql.resolvers.outing import replan_outing_mutation, submit_survey_mutation
from eave.core.graphql.resolvers.reserver_details import submit_reserver_details_mutation


@strawberry.type
class Mutation:
    register = strawberry.mutation(resolver=register_mutation)
    login = strawberry.mutation(resolver=login_mutation)
    refresh_tokens = strawberry.mutation(resolver=refresh_tokens_mutation)
    logout = strawberry.mutation(resolver=logout_mutation)
    submit_survey = strawberry.mutation(resolver=submit_survey_mutation)
    replan_outing = strawberry.mutation(resolver=replan_outing_mutation)
    submit_reserver_details = strawberry.mutation(resolver=submit_reserver_details_mutation)
    create_booking = strawberry.mutation(resolver=create_booking_mutation)
