import strawberry

from eave.core.admin.graphql.resolvers.fields.bookings import admin_get_booking_details_query, admin_list_bookings_query
from eave.core.admin.graphql.resolvers.fields.reserver_details import admin_reserver_details_query
from eave.core.graphql.types.booking import BookingDetailPeek, BookingDetails
from eave.core.graphql.types.reserver_details import ReserverDetails


@strawberry.type
class Query:
    admin_booking: BookingDetails | None = strawberry.field(resolver=admin_get_booking_details_query)
    admin_bookings: list[BookingDetailPeek] = strawberry.field(resolver=admin_list_bookings_query)
    admin_reserver_details: ReserverDetails | None = strawberry.field(resolver=admin_reserver_details_query)
