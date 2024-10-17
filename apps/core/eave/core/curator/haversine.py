# All LA Areas; us_ca_la

from dataclasses import dataclass


@dataclass
class LosAngelesArea:
    name: str
    key: str
    lat: float
    lon: float
    rad: float

LA_AREAS = [
    LosAngelesArea(name="Central LA & Hollywood", key="us_ca_la_1", lat=34.065730, lon=-118.323769, rad=5.78),
    LosAngelesArea(name="Downtown Los Angeles", key="us_ca_la_2", lat=34.046422, lon=-118.245325, rad=1.69),
    LosAngelesArea(name="Pasadena, Glendale, & Northeast LA", key="us_ca_la_3", lat=34.160040, lon=-118.209821, rad=6.49),
    LosAngelesArea(name="Westside", key="us_ca_la_4", lat=33.965090, lon=-118.557344, rad=10.55),
    LosAngelesArea(name="South Bay", key="us_ca_la_5", lat=33.856750, lon=-118.354487, rad=9.70),
    LosAngelesArea(name="San Gabriel Valley", key="us_ca_la_6", lat=34.116746, lon=-118.016725, rad=8.46),
]



import math


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float):
    """https://en.wikipedia.org/wiki/Haversine_formula"""

    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))

    # Radius of Earth in kilometers (mean value)
    r = 6371.0
    return c * r

if __name__ == "__main__":
    eventlat, eventlon = 34.0999764,-118.3293817 # Hollywood

    us_ca_la_1_lat, us_ca_la_1_lon = 34.065730,-118.323769 # Central LA & Hollywood
    us_ca_la_3_lat, us_ca_la_3_lon = 34.160040,-118.209821 # Pasadena, Glendale, & Northeast LA

    distance_from_la_1 = haversine_distance(eventlat, eventlon, us_ca_la_1_lat, us_ca_la_1_lon)
    print(f"Distance from LA-1: {distance_from_la_1:.2f} km")

    distance_from_la_3 = haversine_distance(eventlat, eventlon, us_ca_la_3_lat, us_ca_la_3_lon)
    print(f"Distance from LA-3: {distance_from_la_3:.2f} km")

