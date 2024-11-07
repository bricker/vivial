from enum import StrEnum

import strawberry


@strawberry.enum
class InternalAreaId(StrEnum):
    US_CA_LA1 = "us_ca_la_1"
    US_CA_LA2 = "us_ca_la_2"
    US_CA_LA3 = "us_ca_la_3"
    US_CA_LA4 = "us_ca_la_4"
    US_CA_LA5 = "us_ca_la_5"
    US_CA_LA6 = "us_ca_la_6"


@strawberry.type
class Location:
    internal_area_id: InternalAreaId
    directions_uri: str
    address_1: str
    address_2: str | None
    city: str
    state_code: str
    zip_code: int
    country_code: int
