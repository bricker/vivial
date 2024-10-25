from dataclasses import dataclass

@dataclass
class AddressComponent:
    longText: str
    shortText: str
    types: list[str]
    languageCode: str
