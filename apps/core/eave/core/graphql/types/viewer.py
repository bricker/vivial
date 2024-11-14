import strawberry

from eave.core.graphql.resolvers.fields.booked_outings import list_booked_outings_query
from eave.core.graphql.resolvers.fields.outing import get_outing_query
from eave.core.graphql.resolvers.fields.reserver_details import list_reserver_details_query
from eave.core.graphql.resolvers.mutations.create_booking import create_booking_mutation
from eave.core.graphql.resolvers.mutations.plan_outing import plan_outing_mutation
from eave.core.graphql.resolvers.mutations.refresh_tokens import refresh_tokens_mutation
from eave.core.graphql.resolvers.mutations.replan_outing import replan_outing_mutation
from eave.core.graphql.resolvers.mutations.submit_reserver_details import submit_reserver_details_mutation
from eave.core.graphql.resolvers.mutations.update_account import update_account_mutation
from eave.core.graphql.resolvers.mutations.update_preferences import update_preferences_mutation
from eave.core.graphql.types.outing import Outing
from eave.core.graphql.types.reserver_details import ReserverDetails


@strawberry.type
class Viewer:
    booked_outings: list[Outing] = strawberry.field(resolver=list_booked_outings_query)
    outing: Outing = strawberry.field(resolver=get_outing_query)
    reserver_details: list[ReserverDetails] = strawberry.field(resolver=list_reserver_details_query)

    submit_reserver_details = strawberry.mutation(resolver=submit_reserver_details_mutation)
    create_booking = strawberry.mutation(resolver=create_booking_mutation)
    update_account = strawberry.mutation(resolver=update_account_mutation)
    update_preferences = strawberry.mutation(resolver=update_preferences_mutation)
    refresh_tokens = strawberry.mutation(resolver=refresh_tokens_mutation)
    plan_outing = strawberry.mutation(resolver=plan_outing_mutation)
    replan_outing = strawberry.mutation(resolver=replan_outing_mutation)
