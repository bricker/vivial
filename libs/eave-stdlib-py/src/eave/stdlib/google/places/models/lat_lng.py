from typing import TypedDict


class LatLng(TypedDict, total=False):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#LatLng"""

    latitude: float
    longitude: float
