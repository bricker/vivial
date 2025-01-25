import strawberry

from eave.core.graphql.root.resolvers.mutations.viewer.confirm_booking import confirm_booking_mutation
from eave.core.graphql.root.resolvers.mutations.viewer.initiate_booking import initiate_booking_mutation
from eave.core.graphql.root.resolvers.mutations.viewer.submit_reserver_details import submit_reserver_details_mutation
from eave.core.graphql.root.resolvers.mutations.viewer.update_account import update_account_mutation
from eave.core.graphql.root.resolvers.mutations.viewer.update_outing_preferences import (
    update_outing_preferences_mutation,
)
from eave.core.graphql.root.resolvers.mutations.viewer.update_reserver_details import update_reserver_details_mutation


@strawberry.type
class AuthenticatedViewerMutations:
    submit_reserver_details = strawberry.mutation(resolver=submit_reserver_details_mutation)
    initiate_booking = strawberry.mutation(resolver=initiate_booking_mutation)
    confirm_booking = strawberry.mutation(resolver=confirm_booking_mutation)
    update_account = strawberry.mutation(resolver=update_account_mutation)
    update_preferences = strawberry.mutation(resolver=update_outing_preferences_mutation)
    update_reserver_details = strawberry.mutation(resolver=update_reserver_details_mutation)
    update_outing_preferences = strawberry.mutation(resolver=update_outing_preferences_mutation)
