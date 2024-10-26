from typing import TypedDict
from .fuel_type import FuelType
from .money import Money

class FuelPrice(TypedDict, total=False):
    type: FuelType
    price: Money
    updateTime: str
