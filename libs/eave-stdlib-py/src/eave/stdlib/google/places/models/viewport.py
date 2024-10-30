from typing import TypedDict

from .lat_lng import LatLng


class Viewport(TypedDict, total=False):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#Viewport"""

    low: LatLng
    high: LatLng
