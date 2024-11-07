import strawberry

from eave.core.graphql.types.search_region_code import SearchRegionCode


@strawberry.type
class Location:
    internal_area_id: SearchRegionCode
    directions_uri: str
    address_1: str
    address_2: str | None
    city: str
    state: str
    zip_code: str
