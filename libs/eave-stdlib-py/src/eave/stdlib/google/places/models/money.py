from typing import TypedDict


class Money(TypedDict, total=False):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#Money"""

    currencyCode: str
    units: str
    nanos: int
