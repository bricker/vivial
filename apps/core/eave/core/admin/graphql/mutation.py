
import strawberry

from eave.core.admin.graphql.resolvers.mutations.update_booking import admin_update_booking_mutation


@strawberry.type
class Mutation:
    admin_update_booking = strawberry.mutation(resolver=admin_update_booking_mutation)
