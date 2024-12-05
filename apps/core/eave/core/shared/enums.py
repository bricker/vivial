import enum

import strawberry
from google.maps.places_v1 import PriceLevel

from eave.stdlib.matched_str_enum import MatchedStrEnum

@strawberry.enum
class ActivitySource(MatchedStrEnum):
    INTERNAL = enum.auto()
    EVENTBRITE = enum.auto()
    GOOGLE_PLACES = enum.auto()


@strawberry.enum
class RestaurantSource(MatchedStrEnum):
    GOOGLE_PLACES = enum.auto()


@strawberry.enum
class OutingBudget(MatchedStrEnum):
    FREE = enum.auto()
    INEXPENSIVE = enum.auto()
    MODERATE = enum.auto()
    EXPENSIVE = enum.auto()
    VERY_EXPENSIVE = enum.auto()

    @property
    def upper_limit_cents(self) -> int | None:
        match self:
            case OutingBudget.FREE:
                return 0
            case OutingBudget.INEXPENSIVE:
                return 10 * 100
            case OutingBudget.MODERATE:
                return 50 * 100
            case OutingBudget.EXPENSIVE:
                return 150 * 100
            case OutingBudget.VERY_EXPENSIVE:
                return None

    @property
    def google_places_price_level(self) -> PriceLevel:
        match self:
            case OutingBudget.FREE:
                return PriceLevel.PRICE_LEVEL_FREE
            case OutingBudget.INEXPENSIVE:
                return PriceLevel.PRICE_LEVEL_INEXPENSIVE
            case OutingBudget.MODERATE:
                return PriceLevel.PRICE_LEVEL_MODERATE
            case OutingBudget.EXPENSIVE:
                return PriceLevel.PRICE_LEVEL_EXPENSIVE
            case OutingBudget.VERY_EXPENSIVE:
                return PriceLevel.PRICE_LEVEL_VERY_EXPENSIVE
