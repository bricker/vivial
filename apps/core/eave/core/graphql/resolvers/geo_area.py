import strawberry

from ..types.geo_area import GeoArea
from ..types.search_region_code import SearchRegionCode

MOCK_GEO_AREAS = [
    GeoArea(search_region_code=SearchRegionCode.US_CA_LA1, label="Central LA/Hollywood"),
    GeoArea(search_region_code=SearchRegionCode.US_CA_LA2, label="DTLA"),
    GeoArea(search_region_code=SearchRegionCode.US_CA_LA3, label="Pasadena/Glendale/Northeast LA"),
    GeoArea(search_region_code=SearchRegionCode.US_CA_LA4, label="Westside"),
    GeoArea(search_region_code=SearchRegionCode.US_CA_LA5, label="South Bay"),
    GeoArea(search_region_code=SearchRegionCode.US_CA_LA6, label="SGV"),
]


async def geo_areas_query(*, info: strawberry.Info) -> list[GeoArea]:
    # TODO: Fetch los angeles areas from DB.
    return MOCK_GEO_AREAS
