from dataclasses import dataclass

@dataclass
class Radius:
    miles: float
    meters: float

class GeoArea:
    lat: float | str
    lon: float | str
    rad: Radius
    name: str | None
    key: str | None

    def __init__(self, lat: float | str, lon: float | str, rad_miles: float, name: str | None = None, key: str | None = None) -> None:
        self.lat = lat
        self.lon = lon
        self.rad = Radius(miles=rad_miles, meters=rad_miles*1609.34)
        self.name = name
        self.key = key
