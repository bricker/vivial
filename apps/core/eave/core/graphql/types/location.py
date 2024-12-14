import strawberry

from eave.core.lib.geo import GeoPoint


@strawberry.type
class Location:
    directions_uri: str | None
    coordinates: GeoPoint
    formatted_address: str | None
