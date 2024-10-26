from typing import TypedDict

class Money(TypedDict, total=False):
    currencyCode: str
    units: str
    nanos: int
