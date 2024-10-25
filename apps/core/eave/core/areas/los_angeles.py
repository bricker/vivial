from .geo_area import GeoArea, Radius

# TODO: Convert meters programmatically instead of hardcoding.
us_ca_la_1 = GeoArea(name="Central LA & Hollywood", key="us_ca_la_1", lat=34.065730, lon=-118.323769, rad=(Radius(miles=5.78, meters=9302.008)))
us_ca_la_2 = GeoArea(name="Downtown Los Angeles", key="us_ca_la_2", lat=34.046422, lon=-118.245325, rad=(Radius(miles=1.69, meters=2719.791)))
us_ca_la_3 = GeoArea(name="Pasadena, Glendale, & Northeast LA", key="us_ca_la_3", lat=34.160040, lon=-118.209821, rad=(Radius(miles=6.49, meters=10444.64)))
us_ca_la_4 = GeoArea(name="Westside", key="us_ca_la_4", lat=33.965090, lon=-118.557344, rad=(Radius(miles=10.55, meters=16978.579)))
us_ca_la_5 = GeoArea(name="South Bay", key="us_ca_la_5", lat=33.856750, lon=-118.354487, rad=(Radius(miles=9.70, meters=15610.6)))
us_ca_la_6 = GeoArea(name="San Gabriel Valley", key="us_ca_la_6", lat=34.116746, lon=-118.016725, rad=(Radius(miles=8.46, meters=13615.05)))

LOS_ANGELES_AREAS = [
    us_ca_la_1,
    us_ca_la_2,
    us_ca_la_3,
    us_ca_la_4,
    us_ca_la_5,
    us_ca_la_6,
]

LOS_ANGELES_AREA_MAP = {
    "us_ca_la_1": us_ca_la_1,
    "us_ca_la_2": us_ca_la_2,
    "us_ca_la_3": us_ca_la_3,
    "us_ca_la_4": us_ca_la_4,
    "us_ca_la_5": us_ca_la_5,
    "us_ca_la_6": us_ca_la_6,
}
