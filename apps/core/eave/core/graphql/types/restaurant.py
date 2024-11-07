import strawberry

from eave.core.outing.models.sources import RestaurantSource

from .location import Location
from .photos import Photos


@strawberry.type
class Restaurant:
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
