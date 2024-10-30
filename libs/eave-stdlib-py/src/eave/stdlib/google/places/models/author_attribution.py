from typing import TypedDict


class AuthorAttribution(TypedDict, total=False):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#AuthorAttribution"""

    displayName: str
    uri: str
    photoUri: str
