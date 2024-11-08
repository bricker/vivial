import math
from dataclasses import dataclass
from enum import IntEnum

import geoalchemy2.shape
from geoalchemy2 import WKBElement
from shapely import Point


class SpatialReferenceSystemId(IntEnum):
    LAT_LON = 4326


@dataclass(kw_only=True)
class Distance:
    miles: float

    @property
    def meters(self) -> float:
        return self.miles * 1609.34


@dataclass(kw_only=True)
class GeoPoint:
    lat: float
    lon: float

    def shapely_shape(self) -> Point:
        # lon,lat is the correct order, see: https://postgis.net/documentation/tips/lon-lat-or-lat-lon/
        return Point(self.lon, self.lat)

    def geoalchemy_shape(self) -> WKBElement:
        return geoalchemy2.shape.from_shape(self.shapely_shape(), srid=SpatialReferenceSystemId.LAT_LON, extended=False)


@dataclass(kw_only=True)
class GeoArea:
    center: GeoPoint
    rad: Distance


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """https://en.wikipedia.org/wiki/Haversine_formula"""

    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    # Radius of Earth in kilometers (mean value)
    r = 6371.0
    return c * r
