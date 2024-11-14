import strawberry

from eave.core.graphql.extensions.authentication_extension import AuthenticationExtension
from eave.core.graphql.resolvers.fields.viewer import viewer_query
from eave.core.graphql.resolvers.mutations.create_account import create_account_mutation
from eave.core.graphql.resolvers.mutations.login import login_mutation
from eave.core.graphql.resolvers.mutations.logout import logout_mutation
from eave.core.graphql.resolvers.mutations.plan_outing import plan_outing_mutation
from eave.core.graphql.resolvers.mutations.replan_outing import replan_outing_mutation


@strawberry.type
class Mutation:
    create_account = strawberry.mutation(resolver=create_account_mutation)
    login = strawberry.mutation(resolver=login_mutation)
    logout = strawberry.mutation(resolver=logout_mutation)
    plan_outing = strawberry.mutation(
        resolver=plan_outing_mutation, extensions=[AuthenticationExtension(allow_anonymous=True)]
    )
    replan_outing = strawberry.mutation(
        resolver=replan_outing_mutation, extensions=[AuthenticationExtension(allow_anonymous=True)]
    )
    viewer = strawberry.mutation(resolver=viewer_query, extensions=[AuthenticationExtension()])
    # refresh_tokens = strawberry.mutation(resolver=refresh_tokens_mutation, extensions=[AuthenticationExtension()])
    # submit_reserver_details = strawberry.mutation(
    #     resolver=submit_reserver_details_mutation, extensions=[AuthenticationExtension()]
    # )
    # create_booking = strawberry.mutation(resolver=create_booking_mutation, extensions=[AuthenticationExtension()])
    # update_account = strawberry.mutation(resolver=update_account_mutation, extensions=[AuthenticationExtension()])
    # update_preferences = strawberry.mutation(
    #     resolver=update_preferences_mutation, extensions=[AuthenticationExtension()]
    # )
