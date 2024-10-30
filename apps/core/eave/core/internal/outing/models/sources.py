from enum import StrEnum


class ActivitySource(StrEnum):
    INTERNAL = "INTERNAL"
    EVENTBRITE = "EVENTBRITE"


class RestaurantSource(StrEnum):
    GOOGLE_PLACES = "GOOGLE_PLACES"
