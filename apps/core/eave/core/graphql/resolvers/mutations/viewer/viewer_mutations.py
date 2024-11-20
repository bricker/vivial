import strawberry

from eave.core.graphql.resolvers.mutations.plan_outing import plan_outing_mutation
from eave.core.graphql.resolvers.mutations.replan_outing import replan_outing_mutation
from eave.core.graphql.resolvers.mutations.viewer.create_booking import create_booking_mutation
from eave.core.graphql.resolvers.mutations.viewer.create_payment_intent import create_payment_intent_mutation
from eave.core.graphql.resolvers.mutations.viewer.refresh_tokens import refresh_tokens_mutation
from eave.core.graphql.resolvers.mutations.viewer.submit_reserver_details import submit_reserver_details_mutation
from eave.core.graphql.resolvers.mutations.viewer.update_account import update_account_mutation
from eave.core.graphql.resolvers.mutations.viewer.update_preferences import update_preferences_mutation


@strawberry.type
class ViewerMutations:
    submit_reserver_details = strawberry.mutation(resolver=submit_reserver_details_mutation)
    create_booking = strawberry.mutation(resolver=create_booking_mutation)
    update_account = strawberry.mutation(resolver=update_account_mutation)
    update_preferences = strawberry.mutation(resolver=update_preferences_mutation)
    refresh_tokens = strawberry.mutation(resolver=refresh_tokens_mutation)
    plan_outing = strawberry.mutation(resolver=plan_outing_mutation)
    replan_outing = strawberry.mutation(resolver=replan_outing_mutation)
    create_payment_intent = strawberry.mutation(resolver=create_payment_intent_mutation)
