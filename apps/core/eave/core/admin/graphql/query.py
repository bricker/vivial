from typing import Annotated

import strawberry

from eave.core.admin.graphql.resolvers.fields.bookings import admin_get_booking_details_query, admin_list_bookings_query
from eave.core.graphql.extensions.authentication_extension import AuthenticationExtension, UnauthenticatedViewer
from eave.core.graphql.resolvers.fields.activity_category_groups import list_activity_category_groups_query
from eave.core.graphql.resolvers.fields.outing import get_outing_query
from eave.core.graphql.resolvers.fields.restaurant_categories import list_restaurant_categories_query
from eave.core.graphql.resolvers.fields.search_regions import list_search_regions_query
from eave.core.graphql.resolvers.fields.viewer.viewer_queries import AuthenticatedViewerQueries
from eave.core.graphql.types.activity import ActivityCategoryGroup
from eave.core.graphql.types.booking import BookingDetailPeek, BookingDetails
from eave.core.graphql.types.outing import Outing
from eave.core.graphql.types.restaurant import RestaurantCategory
from eave.core.graphql.types.search_region import SearchRegion


@strawberry.type
class Query:
    booking: BookingDetails | None = strawberry.field(resolver=admin_get_booking_details_query)
    bookings: list[BookingDetailPeek] = strawberry.field(resolver=admin_list_bookings_query)
