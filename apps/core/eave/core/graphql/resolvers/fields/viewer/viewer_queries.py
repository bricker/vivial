import strawberry

from eave.core.graphql.resolvers.fields.outing import get_outing_query
from eave.core.graphql.resolvers.fields.viewer.booked_outings import get_booking_details_query, list_bookings_query
from eave.core.graphql.resolvers.fields.viewer.reserver_details import list_reserver_details_query
from eave.core.graphql.types.booking import BookingDetailPeek, BookingDetails
from eave.core.graphql.types.outing import Outing
from eave.core.graphql.types.reserver_details import ReserverDetails


@strawberry.type
class AuthenticatedViewerQueries:
    booked_outings: list[BookingDetailPeek] = strawberry.field(resolver=list_bookings_query)
    booked_outing: BookingDetails = strawberry.field(resolver=get_booking_details_query)
    outing: Outing = strawberry.field(resolver=get_outing_query)
    reserver_details: list[ReserverDetails] = strawberry.field(resolver=list_reserver_details_query)
