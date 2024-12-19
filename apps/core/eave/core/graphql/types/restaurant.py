from datetime import datetime
from uuid import UUID

import strawberry

from eave.core.graphql.types.cost_breakdown import CostBreakdown
from eave.core.lib.address import format_address
from eave.core.orm.restaurant_category import RestaurantCategoryOrm
from eave.core.shared.enums import RestaurantSource
from eave.stdlib.typing import JsonObject

from .location import Location
from .photos import Photos


@strawberry.type
class Restaurant:
    source_id: str
    source: RestaurantSource
    location: Location
    photos: Photos
    name: str
    reservable: bool
    rating: float
    primary_type_name: str
    website_uri: str | None
    description: str
    parking_tips: str | None
    customer_favorites: str | None


@strawberry.type
class RestaurantCategory:
    id: UUID
    name: str
    is_default: bool

    @classmethod
    def from_orm(cls, orm: RestaurantCategoryOrm) -> "RestaurantCategory":
        return RestaurantCategory(
            id=orm.id,
            name=orm.name,
            is_default=orm.is_default,
        )


@strawberry.type
class Reservation:
    arrival_time: datetime
    headcount: int
    restaurant: Restaurant

    @strawberry.field
    def cost_breakdown(self) -> CostBreakdown:
        return self.calculate_cost_breakdown()

    def calculate_cost_breakdown(self) -> CostBreakdown:
        return CostBreakdown()  # Reservations are currently always free

    def build_analytics_properties(self) -> JsonObject:
        return {
            "start_time": self.arrival_time.isoformat(),
            "category": self.restaurant.primary_type_name,
            "accepts_reservations": self.restaurant.reservable,
            "address": format_address(self.restaurant.location.address.to_address(), singleline=True),
        }
