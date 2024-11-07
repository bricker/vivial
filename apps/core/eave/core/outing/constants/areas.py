from ..models.geo_area import GeoArea
from ..models.search_region_code import SearchRegionCode

us_ca_la_1 = GeoArea(
    name="Central LA/Hollywood", key=SearchRegionCode.US_CA_LA1, lat=34.065730, lon=-118.323769, rad_miles=5.78
)
us_ca_la_2 = GeoArea(name="DTLA", key=SearchRegionCode.US_CA_LA2, lat=34.046422, lon=-118.245325, rad_miles=1.69)
us_ca_la_3 = GeoArea(
    name="Pasadena/Glendale/Northeast LA",
    key=SearchRegionCode.US_CA_LA3,
    lat=34.160040,
    lon=-118.209821,
    rad_miles=6.49,
)
us_ca_la_4 = GeoArea(name="Westside", key=SearchRegionCode.US_CA_LA4, lat=33.965090, lon=-118.557344, rad_miles=10.55)
us_ca_la_5 = GeoArea(name="South Bay", key=SearchRegionCode.US_CA_LA5, lat=33.856750, lon=-118.354487, rad_miles=9.70)
us_ca_la_6 = GeoArea(name="SGV", key=SearchRegionCode.US_CA_LA6, lat=34.116746, lon=-118.016725, rad_miles=8.46)

LOS_ANGELES_AREA_MAP = {
    SearchRegionCode.US_CA_LA1: us_ca_la_1,
    SearchRegionCode.US_CA_LA2: us_ca_la_2,
    SearchRegionCode.US_CA_LA3: us_ca_la_3,
    SearchRegionCode.US_CA_LA4: us_ca_la_4,
    SearchRegionCode.US_CA_LA5: us_ca_la_5,
    SearchRegionCode.US_CA_LA6: us_ca_la_6,
}

LOS_ANGELES_AREAS = [
    us_ca_la_1,
    us_ca_la_2,
    us_ca_la_3,
    us_ca_la_4,
    us_ca_la_5,
    us_ca_la_6,
]
