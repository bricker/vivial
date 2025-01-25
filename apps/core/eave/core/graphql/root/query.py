from typing import Annotated

import strawberry

from eave.core.graphql.extensions.authentication_extension import AuthenticationExtension, UnauthenticatedViewer
from eave.core.graphql.root.resolvers.fields.activity_category_groups import list_activity_category_groups_query
from eave.core.graphql.root.resolvers.fields.outing import get_outing_query
from eave.core.graphql.root.resolvers.fields.restaurant_categories import list_restaurant_categories_query
from eave.core.graphql.root.resolvers.fields.search_regions import list_search_regions_query
from eave.core.graphql.root.resolvers.fields.viewer.viewer_queries import AuthenticatedViewerQueries
from eave.core.graphql.types.activity import ActivityCategoryGroup
from eave.core.graphql.types.outing import Outing
from eave.core.graphql.types.restaurant import RestaurantCategory
from eave.core.graphql.types.search_region import SearchRegion


@strawberry.type
class Query:
    search_regions: list[SearchRegion] = strawberry.field(resolver=list_search_regions_query)
    outing: Outing | None = strawberry.field(resolver=get_outing_query)
    activity_category_groups: list[ActivityCategoryGroup] = strawberry.field(
        resolver=list_activity_category_groups_query
    )
    restaurant_categories: list[RestaurantCategory] = strawberry.field(resolver=list_restaurant_categories_query)

    @strawberry.field(extensions=[AuthenticationExtension()])
    def viewer(
        self,
    ) -> Annotated[AuthenticatedViewerQueries | UnauthenticatedViewer, strawberry.union("ViewerQueries")]:
        return AuthenticatedViewerQueries()
