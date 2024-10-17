from dataclasses import dataclass


@dataclass
class GeoArea:
    name: str
    key: str
    lat: float
    lon: float
    rad: float
