import strawberry

from eave.core.graphql.extensions.authentication_extension import AuthenticationExtension
from eave.core.graphql.resolvers.account import account_query
from eave.core.graphql.resolvers.category import activity_categories_query, restaurant_categories_query
from eave.core.graphql.resolvers.geo_area import geo_areas_query
from eave.core.graphql.resolvers.outing import booked_outings_query, outing_query
from eave.core.graphql.resolvers.reserver_details import reserver_details_query
from eave.core.graphql.resolvers.viewer import viewer_query
from eave.core.graphql.types.account import Account
from eave.core.graphql.types.category import Category
from eave.core.graphql.types.geo_area import GeoArea
from eave.core.graphql.types.outing import Outing
from eave.core.graphql.types.reserver_details import ReserverDetails


@strawberry.type
class Query:
    account: Account = strawberry.field(resolver=account_query)
    activity_categories_query: list[Category] = strawberry.field(resolver=activity_categories_query)
    booked_outings: list[Outing] = strawberry.field(resolver=booked_outings_query)
    geo_areas: list[GeoArea] = strawberry.field(resolver=geo_areas_query)
    outing: Outing = strawberry.field(resolver=outing_query)
    reserver_details: list[ReserverDetails] = strawberry.field(resolver=reserver_details_query)
    restaurant_categories: list[Category] = strawberry.field(resolver=restaurant_categories_query)
    viewer: Account = strawberry.field(resolver=viewer_query, extensions=[AuthenticationExtension()])
