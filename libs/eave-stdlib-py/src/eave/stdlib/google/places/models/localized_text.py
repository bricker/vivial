from typing import TypedDict


class LocalizedText(TypedDict, total=False):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#LocalizedText"""

    text: str
    languageCode: str
