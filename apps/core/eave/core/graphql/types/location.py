import strawberry

from eave.core.shared.geo import GeoPoint
from eave.core.shared.address import Address


@strawberry.type
class Location:
    directions_uri: str | None
    coordinates: GeoPoint
    address: Address
