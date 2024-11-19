import strawberry

from eave.core.graphql.resolvers.fields.booked_outings import list_booked_outings_query
from eave.core.graphql.resolvers.fields.outing import get_outing_query
from eave.core.graphql.resolvers.fields.payment.payment_queries import PaymentQueries
from eave.core.graphql.resolvers.fields.reserver_details import list_reserver_details_query
from eave.core.graphql.types.outing import Outing
from eave.core.graphql.types.reserver_details import ReserverDetails


@strawberry.type
class ViewerQueries:
    booked_outings: list[Outing] = strawberry.field(resolver=list_booked_outings_query)
    outing: Outing = strawberry.field(resolver=get_outing_query)
    reserver_details: list[ReserverDetails] = strawberry.field(resolver=list_reserver_details_query)

    @strawberry.field
    def payment(self) -> PaymentQueries:
        return PaymentQueries()
