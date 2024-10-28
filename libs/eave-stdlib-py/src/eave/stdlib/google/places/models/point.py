from typing import TypedDict

from .date import Date


class Point(TypedDict, total=False):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#Point"""

    date: Date
    truncated: bool
    day: int
    hour: int
    minute: int
