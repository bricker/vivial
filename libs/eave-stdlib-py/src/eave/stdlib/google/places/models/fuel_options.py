from typing import TypedDict

from .fuel_price import FuelPrice


class FuelOptions(TypedDict, total=False):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#FuelOptions"""

    fuelPrices: list[FuelPrice]
