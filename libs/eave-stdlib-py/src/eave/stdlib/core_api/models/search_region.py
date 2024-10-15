from enum import StrEnum
from typing import Self


class SearchRegionCode(StrEnum):
    US_CA_LA = "us_ca_la"
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


class SearchRegion:
    @classmethod
    def from_code(cls, code: SearchRegionCode) -> Self:
        match code:
            case SearchRegionCode.US_CA_LA:
                return cls(
                    code=code,
                    origin_latitude=None,
                    origin_longitude=None,
                    origin_radius_miles=None,
                    description="All of LA",
                )
            case SearchRegionCode.US_CA_LA1:
                return cls(
                    code=code,
                    origin_latitude="34.065730",
                    origin_longitude="-118.323769",
                    origin_radius_miles=5.78,
                    description="Central LA & Hollywood",
                )
            case SearchRegionCode.US_CA_LA2:
                return cls(
                    code=code,
                    origin_latitude="34.046422",
                    origin_longitude="-118.245325",
                    origin_radius_miles=1.69,
                    description="Downtown Los Angeles",
                )
            case SearchRegionCode.US_CA_LA3:
                return cls(
                    code=code,
                    origin_latitude="34.160040",
                    origin_longitude="-118.209821",
                    origin_radius_miles=6.49,
                    description="Pasadena, Glendale, & Northeast LA",
                )
            case SearchRegionCode.US_CA_LA4:
                return cls(
                    code=code,
                    origin_latitude="33.965090",
                    origin_longitude="-118.557344",
                    origin_radius_miles=10.55,
                    description="Westside",
                )
            case SearchRegionCode.US_CA_LA5:
                return cls(
                    code=code,
                    origin_latitude="33.856750",
                    origin_longitude="-118.354487",
                    origin_radius_miles=9.7,
                    description="South Bay",
                )
            case SearchRegionCode.US_CA_LA6:
                return cls(
                    code=code,
                    origin_latitude="34.116746",
                    origin_longitude="-118.016725",
                    origin_radius_miles=8.46,
                    description="San Gabriel Valley",
                )

    def __init__(
        self,
        code: SearchRegionCode,
        origin_latitude: str | None,
        origin_longitude: str | None,
        origin_radius_miles: float | None,
        description: str,
    ) -> None:
        self.code = code
        self.origin_latitude = origin_latitude
        self.origin_longitude = origin_longitude
        self.origin_radius_miles = origin_radius_miles
        self.description = description
