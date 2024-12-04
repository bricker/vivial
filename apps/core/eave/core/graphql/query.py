from typing import Annotated

import strawberry

from eave.core.graphql.extensions.authentication_extension import AuthenticationExtension, UnauthenticatedViewer
from eave.core.graphql.resolvers.fields.activity_categories import list_activity_category_groups_query
from eave.core.graphql.resolvers.fields.restaurant_categories import list_restaurant_categories_query
from eave.core.graphql.resolvers.fields.search_regions import list_search_regions_query
from eave.core.graphql.resolvers.fields.viewer.viewer_queries import AuthenticatedViewerQueries
from eave.core.graphql.types.activity import ActivityCategoryGroup
from eave.core.graphql.types.restaurant import RestaurantCategory
from eave.core.graphql.types.search_region import SearchRegion


@strawberry.type
class Query:
    search_regions: list[SearchRegion] = strawberry.field(resolver=list_search_regions_query)
    activity_categories: list[ActivityCategoryGroup] = strawberry.field(resolver=list_activity_category_groups_query)
    restaurant_categories: list[RestaurantCategory] = strawberry.field(resolver=list_restaurant_categories_query)

    @strawberry.field(extensions=[AuthenticationExtension()])
    def viewer(
        self,
    ) -> Annotated[AuthenticatedViewerQueries | UnauthenticatedViewer, strawberry.union("ViewerQueries")]:
        return AuthenticatedViewerQueries()
