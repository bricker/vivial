from dataclasses import dataclass

from eave.core.areas.search_region_code import SearchRegionCode


@dataclass
class GeoArea:
    name: str
    key: SearchRegionCode
    lat: float
    lon: float
    rad: float
