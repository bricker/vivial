from typing import TypedDict
from .lat_lng import LatLng

class Viewport(TypedDict, total=False):
    low: LatLng
    high: LatLng