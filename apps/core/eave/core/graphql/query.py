import strawberry

from eave.core.graphql.extensions.authentication_extension import AuthenticationExtension
from eave.core.graphql.resolvers.activity_categories import list_activity_categories_query
from eave.core.graphql.resolvers.restaurant_categories import list_restaurant_categories_query
from eave.core.graphql.resolvers.search_regions import list_search_regions_query
from eave.core.graphql.resolvers.viewer import viewer_query
from eave.core.graphql.types.account import Account
from eave.core.graphql.types.activity import ActivityCategory
from eave.core.graphql.types.restaurant import RestaurantCategory
from eave.core.graphql.types.search_region import SearchRegion


@strawberry.type
class Query:
    search_regions: list[SearchRegion] = strawberry.field(resolver=list_search_regions_query)
    activity_categories: list[ActivityCategory] = strawberry.field(resolver=list_activity_categories_query)
    restaurant_categories: list[RestaurantCategory] = strawberry.field(resolver=list_restaurant_categories_query)
    viewer: Account = strawberry.field(resolver=viewer_query, extensions=[AuthenticationExtension()])
