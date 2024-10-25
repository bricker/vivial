from dataclasses import dataclass
from .fuel_type import FuelType
from .money import Money

@dataclass
class FuelPrice:
    type: FuelType
    price: Money
    updateTime: str
