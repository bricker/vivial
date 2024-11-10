from enum import StrEnum
from typing import TypedDict


class AgeRestriction(StrEnum):
    ALL_AGES = "all_ages"
    GTE_12 = "12+"
    GTE_13 = "13+"
    GTE_14 = "14+"
    GTE_15 = "15+"
    GTE_16 = "16+"
    GTE_17 = "17+"
    GTE_18 = "18+"
    GTE_19 = "19+"
    GTE_21 = "21+"
    UNDER_14_WITH_GUARDIAN = "under_14_with_guardian"
    UNDER_16_WITH_GUARDIAN = "under_16_with_guardian"
    UNDER_18_WITH_GUARDIAN = "under_18_with_guardian"
    UNDER_21_WITH_GUARDIAN = "under_21_with_guardian"


class MusicProperties(TypedDict, total=False):
    resource_uri: str

    age_restriction: AgeRestriction | None
    """Minimum age requirement of event attendees."""

    presented_by: str | None
    """Main music event sponsor."""

    door_time: str | None
    """Time relative to UTC that the doors are opened to allow people in the day of the event. When not set the event won't have any door time set."""
