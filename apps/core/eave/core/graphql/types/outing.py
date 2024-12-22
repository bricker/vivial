import random
from datetime import datetime
from uuid import UUID

import strawberry
from google.maps.routing import ComputeRoutesRequest, Location, RouteTravelMode, RoutesAsyncClient, RoutingPreference, Waypoint
import google.type.latlng_pb2

from eave.core.graphql.types.cost_breakdown import CostBreakdown
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
class TravelInfo:
    duration_text: str
    distance_text: str

@strawberry.type
class Outing:
    id: UUID
    survey: Survey | None
    activity_plan: ActivityPlan | None
    reservation: Reservation | None

    @strawberry.field
    def search_regions(self) -> list[SearchRegion]:
        search_regions: dict[UUID, SearchRegion] = {}

        if self.activity_plan:
            r = self.activity_plan.activity.venue.location.find_closest_search_region()
            search_regions[r.id] = r

        if self.reservation:
            r = self.reservation.restaurant.location.find_closest_search_region()
            search_regions[r.id] = r

        return list(search_regions.values())

    @strawberry.field
    def headcount(self) -> int:
        headcount = 0

        if self.reservation:
            headcount = max(headcount, self.reservation.headcount)

        if self.activity_plan:
            headcount = max(headcount, self.activity_plan.headcount)

        if headcount == 0:
            raise ValueError("invalid headcount 0")

        return headcount

    @strawberry.field
    def start_time(self) -> datetime:
        if self.reservation:
            return self.reservation.arrival_time
        elif self.activity_plan:
            return self.activity_plan.start_time
        else:
            raise ValueError("both reservation and activity_plan are None")

    @strawberry.field
    async def travel(self) -> TravelInfo | None:
        if not self.reservation or not self.activity_plan or self.reservation.restaurant.source != RestaurantSource.GOOGLE_PLACES:
            return None

        routes_request = ComputeRoutesRequest(
            origin=Waypoint(
                place_id=self.reservation.restaurant.source_id,
            ),
            destination=Waypoint(
                location=Location(
                    lat_lng=google.type.latlng_pb2.LatLng( # type: ignore - protobuf types can't be found by the static analyzer
                        latitude=self.activity_plan.activity.venue.location.coordinates.lat,
                        longitude=self.activity_plan.activity.venue.location.coordinates.lon,
                    ),
                ),
            ),
            travel_mode=RouteTravelMode.DRIVE,
            routing_preferences=RoutingPreference.TRAFFIC_AWARE,
            arrival_time=self.activity_plan.start_time,
            # departure_time=self.reservation.departure_time,
        )

        response = await GOOGLE_MAPS_ROUTING_API_CLIENT.compute_routes(routes_request)
        if len(response.routes) == 0:
            return None

        best_route = response.routes[0]
        return TravelInfo(
            duration_text=best_route.localized_values.duration,
            distance_text=best_route.localized_values.distance,
        )

    @strawberry.field
    def cost_breakdown(self) -> CostBreakdown:
        return self.calculate_cost_breakdown()

    def calculate_cost_breakdown(self) -> CostBreakdown:
        cb = CostBreakdown()

        if self.activity_plan:
            cb += self.activity_plan.calculate_cost_breakdown()

        if self.reservation:
            cb += self.reservation.calculate_cost_breakdown()

        return cb
