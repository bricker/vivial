from enum import StrEnum


class EventSource(StrEnum):
    INTERNAL = "INTERNAL"
    EVENTBRITE = "EVENTBRITE"
    GOOGLE_PLACES = "GOOGLE_PLACES"
