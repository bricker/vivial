import strawberry

from eave.core.graphql.types.address import GraphQLAddress
from eave.core.shared.geo import GeoPoint


@strawberry.type
class Location:
    directions_uri: str | None
    coordinates: GeoPoint
    address: GraphQLAddress
