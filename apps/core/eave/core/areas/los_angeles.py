from eave.core.areas.search_region_code import SearchRegionCode

from .geo_area import GeoArea

LOS_ANGELES_AREAS = [
    GeoArea(name="Central LA & Hollywood", key=SearchRegionCode.US_CA_LA1, lat=34.065730, lon=-118.323769, rad=5.78),
    GeoArea(name="Downtown Los Angeles", key=SearchRegionCode.US_CA_LA2, lat=34.046422, lon=-118.245325, rad=1.69),
    GeoArea(
        name="Pasadena, Glendale, & Northeast LA",
        key=SearchRegionCode.US_CA_LA3,
        lat=34.160040,
        lon=-118.209821,
        rad=6.49,
    ),
    GeoArea(name="Westside", key=SearchRegionCode.US_CA_LA4, lat=33.965090, lon=-118.557344, rad=10.55),
    GeoArea(name="South Bay", key=SearchRegionCode.US_CA_LA5, lat=33.856750, lon=-118.354487, rad=9.70),
    GeoArea(name="San Gabriel Valley", key=SearchRegionCode.US_CA_LA6, lat=34.116746, lon=-118.016725, rad=8.46),
]
