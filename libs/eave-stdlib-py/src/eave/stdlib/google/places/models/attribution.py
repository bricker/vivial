from typing import TypedDict


class Attribution(TypedDict, total=False):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#Attribution"""

    provider: str
    providerUri: str
