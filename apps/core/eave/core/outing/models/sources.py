from enum import StrEnum

import strawberry


@strawberry.enum
class ActivitySource(StrEnum):
    INTERNAL = "INTERNAL"
    EVENTBRITE = "EVENTBRITE"


@strawberry.enum
class RestaurantSource(StrEnum):
    GOOGLE_PLACES = "GOOGLE_PLACES"
