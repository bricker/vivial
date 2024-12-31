import math

import geoalchemy2.shape
import strawberry
from geoalchemy2 import WKBElement
from shapely import Point

from eave.core.lib.geo import SpatialReferenceSystemId


@strawberry.type
class GeoPoint:
    lat: float
    lon: float

    def shapely_shape(self) -> Point:
        # lon,lat is the correct order, see: https://postgis.net/documentation/tips/lon-lat-or-lat-lon/
        return Point(self.lon, self.lat)

    def geoalchemy_shape(self) -> WKBElement:
        return geoalchemy2.shape.from_shape(self.shapely_shape(), srid=SpatialReferenceSystemId.LAT_LON, extended=False)

    def expand_rect(self, *, miles: float) -> tuple["GeoPoint", "GeoPoint"]:
        latdegrees = miles/69
        londegrees = latdegrees / math.cos(self.lat)
        return (
            GeoPoint(
                lat=self.lat-latdegrees,
                lon=self.lon-londegrees
            ),
            GeoPoint(
                lat=self.lat+latdegrees,
                lon=self.lon+londegrees,
            ),
        )

    def haversine_distance(self, to_point: "GeoPoint") -> float:
        """
        Returns the distance between `self` and `to_point` measured in miles.
        https://en.wikipedia.org/wiki/Haversine_formula
        """
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [self.lat, self.lon, to_point.lat, to_point.lon])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))

        # Radius of Earth in miles (mean value)
        r = 3958.75
        return c * r


@strawberry.type
class Distance:
    miles: float
    meters: float

    def __init__(self, *, miles: float) -> None:
        self.miles = miles
        self.meters = miles * 1609.34


@strawberry.type
class GeoArea:
    center: GeoPoint
    rad: Distance
