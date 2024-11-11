from uuid import UUID

import strawberry


@strawberry.type
class Location:
    search_region_id: UUID
    directions_uri: str
    address_1: str
    address_2: str | None
    city: str
    state: str
    zip_code: str
