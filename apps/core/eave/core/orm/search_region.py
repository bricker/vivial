import math
from dataclasses import dataclass
from types import MappingProxyType
from uuid import UUID

from eave.core.shared.geo import Distance, GeoArea, GeoPoint


@dataclass(kw_only=True, frozen=True)
class SearchRegionOrm:
    id: UUID
    name: str
    area: GeoArea

    @classmethod
    def all(cls) -> list["SearchRegionOrm"]:
        return list(_SEARCH_REGIONS_TABLE)

    @classmethod
    def one_or_exception(cls, *, search_region_id: UUID) -> "SearchRegionOrm":
        return _SEARCH_REGIONS_PK[search_region_id]

    @classmethod
    def get_closest(
        cls,
        *,
        point: GeoPoint,
    ) -> "SearchRegionOrm":
        """
        From all search regions, return the one that is closest to `point`.
        """
        closest_region = _SEARCH_REGIONS_TABLE[0]
        activity_curr_min_dist = math.inf

        for region in SearchRegionOrm.all():
            # see if dist to `activity` from `region` is less than from current closest `activity_region`
            dist_from_region_center = point.haversine_distance(to_point=region.area.center)
            if dist_from_region_center < activity_curr_min_dist:
                activity_curr_min_dist = dist_from_region_center
                closest_region = region

        return closest_region


_SEARCH_REGIONS_TABLE = (
    SearchRegionOrm(
        id=UUID("354c2020-6227-46c1-be04-6f5965ba452d"),
        name="Central LA/Hollywood",
        area=GeoArea(
            center=GeoPoint(lat=34.065730, lon=-118.323769),
            rad=Distance(miles=5.78),
        ),
    ),
    SearchRegionOrm(
        id=UUID("94d05616-887a-440e-a2c5-c06ece510877"),
        name="DTLA",
        area=GeoArea(
            center=GeoPoint(lat=34.046422, lon=-118.245325),
            rad=Distance(miles=1.69),
        ),
    ),
    SearchRegionOrm(
        id=UUID("5b8c5453-2404-4510-87c9-2e9aba6cdce7"),
        name="Pasadena/Glendale/Northeast LA",
        area=GeoArea(
            center=GeoPoint(lat=34.160040, lon=-118.209821),
            rad=Distance(miles=6.49),
        ),
    ),
    SearchRegionOrm(
        id=UUID("ebdcdb09-ac97-4b63-a7e1-c3c09f49eae4"),
        name="Westside",
        area=GeoArea(
            center=GeoPoint(lat=33.965090, lon=-118.557344),
            rad=Distance(miles=10.55),
        ),
    ),
    SearchRegionOrm(
        id=UUID("1941f517-d7fc-4805-ad63-24214130dbc7"),
        name="South Bay",
        area=GeoArea(
            center=GeoPoint(lat=33.856750, lon=-118.354487),
            rad=Distance(miles=9.70),
        ),
    ),
    SearchRegionOrm(
        id=UUID("e3b49a70-0df0-4d80-a7c6-1ad1a684cdc2"),
        name="SGV",
        area=GeoArea(
            center=GeoPoint(lat=34.116746, lon=-118.016725),
            rad=Distance(miles=8.46),
        ),
    ),
)

_SEARCH_REGIONS_PK = MappingProxyType({region.id: region for region in _SEARCH_REGIONS_TABLE})
