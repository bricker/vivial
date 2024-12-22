from datetime import datetime
from uuid import UUID

import google.type.latlng_pb2
import strawberry
from google.maps.routing import (
    ComputeRoutesRequest,
    Location,
    RouteTravelMode,
    RoutingPreference,
    Waypoint,
)

from eave.core.graphql.types.cost_breakdown import CostBreakdown
from eave.core.graphql.types.itinerary import Itinerary
from eave.core.graphql.types.search_region import SearchRegion
from eave.core.graphql.types.survey import Survey
from eave.core.lib.api_clients import GOOGLE_MAPS_ROUTING_API_CLIENT
from eave.core.shared.enums import RestaurantSource

from .activity import ActivityPlan
from .restaurant import Reservation


@strawberry.input
class OutingPreferencesInput:
    restaurant_category_ids: list[UUID]
    activity_category_ids: list[UUID]

@strawberry.type
class Outing(Itinerary):
    pass
