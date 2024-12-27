import strawberry

from eave.core.graphql.resolvers.fields.viewer.account import get_viewer_account_query
from eave.core.graphql.resolvers.fields.viewer.billing_portal_url import get_billing_portal_url_query
from eave.core.graphql.resolvers.fields.viewer.booked_outings import get_booking_details_query, list_bookings_query
from eave.core.graphql.resolvers.fields.viewer.outing_preferences import (
    OutingPreferences,
    get_outing_preferences_query,
)
from eave.core.graphql.resolvers.fields.viewer.payment_methods import list_viewer_payment_methods_query
from eave.core.graphql.resolvers.fields.viewer.reserver_details import list_reserver_details_query
from eave.core.graphql.types.account import Account
from eave.core.graphql.types.booking import BookingDetails, BookingDetailsPeek
from eave.core.graphql.types.reserver_details import ReserverDetails
from eave.core.graphql.types.stripe import PaymentMethod


@strawberry.type
class AuthenticatedViewerQueries:
    booked_outings: list[BookingDetailsPeek] = strawberry.field(resolver=list_bookings_query)
    booked_outing_details: BookingDetails | None = strawberry.field(resolver=get_booking_details_query)
    reserver_details: list[ReserverDetails] = strawberry.field(resolver=list_reserver_details_query)
    outing_preferences: OutingPreferences = strawberry.field(resolver=get_outing_preferences_query)
    account: Account = strawberry.field(resolver=get_viewer_account_query)
    payment_methods: list[PaymentMethod] = strawberry.field(resolver=list_viewer_payment_methods_query)
    billing_portal_url: str = strawberry.field(resolver=get_billing_portal_url_query)
