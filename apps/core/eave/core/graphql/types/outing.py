import enum
from datetime import datetime
from typing import Annotated
from uuid import UUID

from google.maps.places_v1 import PriceLevel
import strawberry

from eave.core.graphql.types.user import UserInput

from .activity import Activity
from .restaurant import Restaurant


@strawberry.enum
class OutingState(enum.Enum):
    PAST = enum.auto()
    FUTURE = enum.auto()


@strawberry.enum
class OutingBudget(enum.Enum):
    ZERO = enum.auto()
    ONE = enum.auto()
    TWO = enum.auto()
    THREE = enum.auto()
    FOUR = enum.auto()

    @property
    def upper_limit_cents(self) -> int | None:
        match self:
            case OutingBudget.ZERO:
                return 0
            case OutingBudget.ONE:
                return 10 * 100
            case OutingBudget.TWO:
                return 50 * 100
            case OutingBudget.THREE:
                return 150 * 100
            case OutingBudget.FOUR:
                return None

    @property
    def google_places_price_level(self) -> PriceLevel:
        match self:
            case OutingBudget.ZERO:
                return PriceLevel.PRICE_LEVEL_FREE
            case OutingBudget.ONE:
                return PriceLevel.PRICE_LEVEL_INEXPENSIVE
            case OutingBudget.TWO:
                return PriceLevel.PRICE_LEVEL_MODERATE
            case OutingBudget.THREE:
                return PriceLevel.PRICE_LEVEL_EXPENSIVE
            case OutingBudget.FOUR:
                return PriceLevel.PRICE_LEVEL_VERY_EXPENSIVE

@strawberry.type
class Outing:
    id: UUID
    visitor_id: UUID
    account_id: UUID | None
    survey_id: UUID
    budget: OutingBudget
    headcount: int
    activity: Activity | None
    activity_start_time: datetime | None
    restaurant: Restaurant | None
    restaurant_arrival_time: datetime | None
    driving_time: str
