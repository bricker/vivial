import strawberry

from eave.core.graphql.admin.resolvers.fields.bookings import (
    AdminBookingInfo,
    admin_get_booking_activity_query,
    admin_get_booking_info_query,
    admin_get_booking_restaurant_query,
    admin_list_bookings_query,
)
from eave.core.graphql.admin.resolvers.fields.reserver_details import admin_reserver_details_query
from eave.core.graphql.types.activity import Activity
from eave.core.graphql.types.booking import BookingDetailsPeek
from eave.core.graphql.types.reserver_details import ReserverDetails
from eave.core.graphql.types.restaurant import Restaurant


@strawberry.type
class Query:
    admin_booking: AdminBookingInfo | None = strawberry.field(resolver=admin_get_booking_info_query)
    admin_booking_activity_detail: Activity | None = strawberry.field(resolver=admin_get_booking_activity_query)
    admin_booking_restaurant_detail: Restaurant | None = strawberry.field(resolver=admin_get_booking_restaurant_query)
    admin_bookings: list[BookingDetailsPeek] = strawberry.field(resolver=admin_list_bookings_query)
    admin_reserver_details: ReserverDetails | None = strawberry.field(resolver=admin_reserver_details_query)
