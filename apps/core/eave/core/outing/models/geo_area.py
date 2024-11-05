from dataclasses import dataclass

from shapely import to_wkb, Point


@dataclass
class Radius:
    miles: float

    @property
    def meters(self) -> float:
        return self.miles * 1609.34

class GeoArea:
    lat: float
    lon: float
    center: Point
    rad: Radius
    name: str | None
    key: str | None

    def __init__(
        self, lat: float, lon: float, rad_miles: float, name: str | None = None, key: str | None = None
    ) -> None:
        self.lat = lat
        self.lon = lon
        self.center = Point(self.lon, self.lat) # lon,lat is the correct order. see: https://postgis.net/documentation/tips/lon-lat-or-lat-lon/
        self.rad = Radius(miles=rad_miles)
        self.name = name
        self.key = key
