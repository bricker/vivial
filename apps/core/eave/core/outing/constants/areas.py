from ...graphql.types.search_region_code import SearchRegionCode
from ..models.geo_area import GeoArea

LOS_ANGELES_AREA_MAP = {
    SearchRegionCode.US_CA_LA1: GeoArea(
        name="Central LA/Hollywood",
        key=SearchRegionCode.US_CA_LA1,
        lat=34.065730,
        lon=-118.323769,
        rad_miles=5.78,
    ),
    SearchRegionCode.US_CA_LA2: GeoArea(
        name="DTLA",
        key=SearchRegionCode.US_CA_LA2,
        lat=34.046422,
        lon=-118.245325,
        rad_miles=1.69,
    ),
    SearchRegionCode.US_CA_LA3: GeoArea(
        name="Pasadena/Glendale/Northeast LA",
        key=SearchRegionCode.US_CA_LA3,
        lat=34.160040,
        lon=-118.209821,
        rad_miles=6.49,
    ),
    SearchRegionCode.US_CA_LA4: GeoArea(
        name="Westside",
        key=SearchRegionCode.US_CA_LA4,
        lat=33.965090,
        lon=-118.557344,
        rad_miles=10.55,
    ),
    SearchRegionCode.US_CA_LA5: GeoArea(
        name="South Bay",
        key=SearchRegionCode.US_CA_LA5,
        lat=33.856750,
        lon=-118.354487,
        rad_miles=9.70,
    ),
    SearchRegionCode.US_CA_LA6: GeoArea(
        name="SGV",
        key=SearchRegionCode.US_CA_LA6,
        lat=34.116746,
        lon=-118.016725,
        rad_miles=8.46,
    ),
}

LOS_ANGELES_AREAS = LOS_ANGELES_AREA_MAP.values()
