from typing import TypedDict

from .fuel_type import FuelType
from .money import Money


class FuelPrice(TypedDict, total=False):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#FuelPrice"""

    type: FuelType
    price: Money
    updateTime: str
