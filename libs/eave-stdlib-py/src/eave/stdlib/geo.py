import math
from enum import IntEnum


class SpatialReferenceSystemId(IntEnum):
    LAT_LON = 4326


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
