from enum import StrEnum
from typing import Self


class EventSource(StrEnum):
    INTERNAL = "INTERNAL"
    EVENTBRITE = "EVENTBRITE"
    GOOGLE_PLACES = "GOOGLE_PLACES"

    @classmethod
    def from_str(cls, s: str) -> Self | None:
        try:
            return cls.__call__(value=s.lower())
        except ValueError:
            return None
