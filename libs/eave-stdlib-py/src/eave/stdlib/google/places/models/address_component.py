from typing import TypedDict

class AddressComponent(TypedDict, total=False):
    longText: str
    shortText: str
    types: list[str]
    languageCode: str
