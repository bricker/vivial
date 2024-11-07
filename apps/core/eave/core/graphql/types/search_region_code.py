from enum import StrEnum
from typing import Self

import strawberry


@strawberry.enum
class SearchRegionCode(StrEnum):
    US_CA_LA1 = "US_CA_LA1"
    US_CA_LA2 = "US_CA_LA2"
    US_CA_LA3 = "US_CA_LA3"
    US_CA_LA4 = "US_CA_LA4"
    US_CA_LA5 = "US_CA_LA5"
    US_CA_LA6 = "US_CA_LA6"

    @classmethod
    def from_str(cls, s: str) -> Self | None:
        try:
            return cls.__call__(value=s.lower())
        except ValueError:
            return None
