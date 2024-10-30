from typing import TypedDict


class AddressComponent(TypedDict, total=False):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#AddressComponent"""

    longText: str
    shortText: str
    types: list[str]
    languageCode: str
