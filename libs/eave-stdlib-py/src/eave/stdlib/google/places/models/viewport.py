from dataclasses import dataclass
from .lat_lng import LatLng

@dataclass
class Viewport:
    low: LatLng
    high: LatLng