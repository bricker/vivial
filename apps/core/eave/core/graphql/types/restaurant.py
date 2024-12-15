from uuid import UUID

import strawberry

from eave.core.orm.restaurant_category import RestaurantCategoryOrm
from eave.core.shared.enums import RestaurantSource

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
