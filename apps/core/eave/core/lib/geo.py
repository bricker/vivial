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
