from uuid import UUID

import strawberry


@strawberry.type
class Location:
    directions_uri: str
    latitude: float
    longitude: float
    formatted_address: str
