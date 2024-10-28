from typing import TypedDict


class Date(TypedDict, total=False):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#Date"""

    year: int
    month: int
    day: int
