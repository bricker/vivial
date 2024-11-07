from dataclasses import dataclass

from shapely import Point

from eave.core.lib.geo import Distance, GeoLocation


class GeoArea:
    center: GeoLocation
    rad: Distance
    name: str | None
    key: str | None

    def __init__(
        self, lat: float, lon: float, rad_miles: float, name: str | None = None, key: str | None = None
    ) -> None:
        self.center = GeoLocation(lat=lat, lon=lon)
        self.rad = Distance(miles=rad_miles)
        self.name = name
        self.key = key
