from enum import StrEnum
from typing import TypedDict


class AgeRestriction(StrEnum):
    all_ages = "all_ages"
    gte_12 = "12+"
    gte_13 = "13+"
    gte_14 = "14+"
    gte_15 = "15+"
    gte_16 = "16+"
    gte_17 = "17+"
    gte_18 = "18+"
    gte_19 = "19+"
    gte_21 = "21+"
    under_14_with_guardian = "under_14_with_guardian"
    under_16_with_guardian = "under_16_with_guardian"
    under_18_with_guardian = "under_18_with_guardian"
    under_21_with_guardian = "under_21_with_guardian"


class MusicProperties(TypedDict, total=False):
    resource_uri: str | None

    age_restriction: AgeRestriction | None
    """Minimum age requirement of event attendees."""

    presented_by: str | None
    """Main music event sponsor."""

    door_time: str | None
    """Time relative to UTC that the doors are opened to allow people in the day of the event. When not set the event won't have any door time set."""
