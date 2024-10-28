from typing import TypedDict

from .review import Review


class References(TypedDict, total=False):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#References"""

    reviews: list[Review]
    places: list[str]
