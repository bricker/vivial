from eave.core.lib.geo import Distance, GeoArea, GeoPoint

from ..models.search_region import SearchRegion, SearchRegionCode

ALL_AREAS = {
    SearchRegionCode.US_CA_LA1: SearchRegion(
        name="Central LA & Hollywood",
        key=SearchRegionCode.US_CA_LA1,
        area=GeoArea(
            center=GeoPoint(lat=34.065730, lon=-118.323769),
            rad=Distance(miles=5.78),
        ),
    ),
    SearchRegionCode.US_CA_LA2: SearchRegion(
        name="Downtown Los Angeles",
        key=SearchRegionCode.US_CA_LA2,
        area=GeoArea(
            center=GeoPoint(lat=34.046422, lon=-118.245325),
            rad=Distance(miles=1.69),
        ),
    ),
    SearchRegionCode.US_CA_LA3: SearchRegion(
        name="Pasadena, Glendale, & Northeast LA",
        key=SearchRegionCode.US_CA_LA3,
        area=GeoArea(
            center=GeoPoint(lat=34.160040, lon=-118.209821),
            rad=Distance(miles=6.49),
        ),
    ),
    SearchRegionCode.US_CA_LA4: SearchRegion(
        name="Westside",
        key=SearchRegionCode.US_CA_LA4,
        area=GeoArea(
            center=GeoPoint(lat=33.965090, lon=-118.557344),
            rad=Distance(miles=10.55),
        ),
    ),
    SearchRegionCode.US_CA_LA5: SearchRegion(
        name="South Bay",
        key=SearchRegionCode.US_CA_LA5,
        area=GeoArea(
            center=GeoPoint(lat=33.856750, lon=-118.354487),
            rad=Distance(miles=9.70),
        ),
    ),
    SearchRegionCode.US_CA_LA6: SearchRegion(
        name="San Gabriel Valley",
        key=SearchRegionCode.US_CA_LA6,
        area=GeoArea(
            center=GeoPoint(lat=34.116746, lon=-118.016725),
            rad=Distance(miles=8.46),
        ),
    ),
}
