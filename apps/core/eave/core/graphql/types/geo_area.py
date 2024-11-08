import strawberry

from eave.core.outing.models.search_region_code import SearchRegionCode


@strawberry.type
class GeoArea:
    search_region_code: SearchRegionCode
    label: str
