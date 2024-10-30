from enum import StrEnum


class PriceLevel(StrEnum):
    """https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places#PriceLevel"""

    PRICE_LEVEL_UNSPECIFIED = "PRICE_LEVEL_UNSPECIFIED"
    PRICE_LEVEL_FREE = "PRICE_LEVEL_FREE"
    PRICE_LEVEL_INEXPENSIVE = "PRICE_LEVEL_INEXPENSIVE"
    PRICE_LEVEL_MODERATE = "PRICE_LEVEL_MODERATE"
    PRICE_LEVEL_EXPENSIVE = "PRICE_LEVEL_EXPENSIVE"
    PRICE_LEVEL_VERY_EXPENSIVE = "PRICE_LEVEL_VERY_EXPENSIVE"
