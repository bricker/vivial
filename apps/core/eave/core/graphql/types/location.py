import strawberry


@strawberry.type
class Location:
    directions_uri: str | None
    latitude: float
    longitude: float
    formatted_address: str
