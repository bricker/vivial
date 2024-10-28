from typing import TypedDict

from .date import Date


class SpecialDay(TypedDict, total=False):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#SpecialDay"""

    date: Date
