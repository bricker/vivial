from typing import TypedDict

from .author_attribution import AuthorAttribution


class Photo(TypedDict, total=False):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#Photo"""

    name: str
    widthPx: int
    heightPx: int
    authorAttributions: list[AuthorAttribution]
