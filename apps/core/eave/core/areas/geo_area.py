from dataclasses import dataclass

@dataclass
class Radius:
    miles: float
    meters: float

@dataclass
class GeoArea:
    name: str
    key: str
    lat: float
    lon: float
    rad: Radius
