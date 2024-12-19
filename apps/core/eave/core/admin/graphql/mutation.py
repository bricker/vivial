import strawberry

from eave.core.admin.graphql.resolvers.mutations.update_booking import admin_update_booking_mutation
from eave.core.admin.graphql.resolvers.mutations.update_reserver_details import admin_update_reserver_details_mutation


@strawberry.type
class Mutation:
    admin_update_booking = strawberry.mutation(resolver=admin_update_booking_mutation)
    admin_update_reserver_details = strawberry.mutation(resolver=admin_update_reserver_details_mutation)
