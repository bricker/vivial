from dataclasses import dataclass
import json


@dataclass
class GeoArea:
    name: str
    key: str
    lat: float
    lon: float
    rad: float

with open("../data/areas.json") as f:
    AREAS = [GeoArea(**j) for j in json.loads(f.read())]
