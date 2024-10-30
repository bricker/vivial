from typing import TypedDict


class SubDestination(TypedDict, total=False):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#SubDestination"""

    name: str
    id: str
