import strawberry

from eave.core.graphql.resolvers.fields.viewer.booked_outings import get_booking_details_query, list_bookings_query
from eave.core.graphql.resolvers.fields.viewer.outing_preferences import (
    OutingPreferences,
    list_outing_preferences_query,
)
from eave.core.graphql.resolvers.fields.viewer.reserver_details import list_reserver_details_query
from eave.core.graphql.resolvers.fields.viewer.stripe_portal import get_stripe_portal_query
from eave.core.graphql.types.booking import BookingDetailPeek, BookingDetails
from eave.core.graphql.types.reserver_details import ReserverDetails
from eave.core.graphql.types.stripe_portal import StripePortal


@strawberry.type
class AuthenticatedViewerQueries:
    booked_outings: list[BookingDetailPeek] = strawberry.field(resolver=list_bookings_query)
    booked_outing_details: BookingDetails = strawberry.field(resolver=get_booking_details_query)
    reserver_details: list[ReserverDetails] = strawberry.field(resolver=list_reserver_details_query)
    outing_preferences: OutingPreferences = strawberry.field(resolver=list_outing_preferences_query)
    stripe_portal: StripePortal = strawberry.field(resolver=get_stripe_portal_query)
