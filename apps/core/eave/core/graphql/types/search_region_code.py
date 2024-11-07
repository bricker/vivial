from enum import StrEnum
from typing import Self
import strawberry


@strawberry.enum
class SearchRegionCode(StrEnum):
    US_CA_LA1 = "us_ca_la_1"
    US_CA_LA2 = "us_ca_la_2"
    US_CA_LA3 = "us_ca_la_3"
    US_CA_LA4 = "us_ca_la_4"
    US_CA_LA5 = "us_ca_la_5"
    US_CA_LA6 = "us_ca_la_6"

    @classmethod
    def from_str(cls, s: str) -> Self | None:
        try:
            return cls.__call__(value=s.lower())
        except ValueError:
            return None
