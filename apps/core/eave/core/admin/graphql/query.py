
import strawberry

from eave.core.admin.graphql.resolvers.fields.bookings import admin_get_booking_details_query, admin_list_bookings_query
from eave.core.graphql.types.booking import BookingDetailPeek, BookingDetails


@strawberry.type
class Query:
    admin_booking: BookingDetails | None = strawberry.field(resolver=admin_get_booking_details_query)
    admin_bookings: list[BookingDetailPeek] = strawberry.field(resolver=admin_list_bookings_query)
