from dataclasses import dataclass
from .fuel_price import FuelPrice

@dataclass
class FuelOptions:
    fuelPrices: list[FuelPrice]
