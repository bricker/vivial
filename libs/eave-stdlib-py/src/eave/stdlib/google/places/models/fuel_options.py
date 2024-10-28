from typing import TypedDict

from .fuel_price import FuelPrice


class FuelOptions(TypedDict, total=False):
    fuelPrices: list[FuelPrice]
