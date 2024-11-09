import strawberry

from .search_region import SearchRegionCode


@strawberry.type
class GeoArea:
    search_region_code: SearchRegionCode
    label: str
