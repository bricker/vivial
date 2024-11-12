import enum
from uuid import UUID

import strawberry

from eave.core.graphql.types.event_source import EventSource
from eave.core.orm.restaurant_category import RestaurantCategoryOrm

from .location import Location
from .photos import Photos


@strawberry.type
class Restaurant:
    source: EventSource
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

    @classmethod
    def from_orm(cls, orm: RestaurantCategoryOrm) -> "RestaurantCategory":
        return RestaurantCategory(
            id=orm.id,
            name=orm.name,
        )
