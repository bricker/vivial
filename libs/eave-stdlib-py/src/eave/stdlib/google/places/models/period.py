from typing import TypedDict

from .point import Point


class Period(TypedDict, total=False):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#Period"""

    open: Point
    close: Point
