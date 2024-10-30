from enum import StrEnum


class ActivitySource(StrEnum):
    SELF = "SELF"
    EVENTBRITE = "EVENTBRITE"


class ReservationSource(StrEnum):
    SELF = "SELF"
    GOOGLE_PLACES = "GOOGLE_PLACES"
