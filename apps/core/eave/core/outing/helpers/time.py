from datetime import datetime
from enum import StrEnum

class TimeCategory(StrEnum):
    EARLY_MORNING = "EARLY_MORNING"
    LATE_MORNING = "LATE_MORNING"
    EARLY_AFTERNOON = "EARLY_AFTERNOON"
    LATE_AFTERNOON = "LATE_AFTERNOON"
    EARLY_EVENING = "EARLY_EVENING"
    LATE_EVENING = "LATE_EVENING"


def get_time_category(hour: int) -> TimeCategory:
    if hour < 4:
        return TimeCategory.LATE_EVENING # midnight - 3:59 AM

    if hour < 9:
        return TimeCategory.EARLY_MORNING # 4:00 AM - 8:59 AM

    if hour < 12:
        return TimeCategory.LATE_MORNING # 9:00 AM - 11:59 AM

    if hour < 15:
        return TimeCategory.EARLY_AFTERNOON # 12:00 PM - 2:59 PM

    if hour < 18:
        return TimeCategory.LATE_AFTERNOON # 3:00 PM - 5:59 PM

    if hour < 21:
        return TimeCategory.EARLY_EVENING # 6:00 PM - 8:59 PM

    return TimeCategory.LATE_EVENING # 9:00 PM - 11:59 PM


def is_early_morning(timestamp: datetime) -> bool:
    return get_time_category(timestamp.hour) == TimeCategory.EARLY_MORNING


def is_late_morning(timestamp: datetime) -> bool:
    return get_time_category(timestamp.hour) == TimeCategory.LATE_MORNING


def is_early_afternoon(timestamp: datetime) -> bool:
    return get_time_category(timestamp.hour) == TimeCategory.EARLY_AFTERNOON


def is_late_afternoon(timestamp: datetime) -> bool:
    return get_time_category(timestamp.hour) == TimeCategory.LATE_AFTERNOON


def is_early_evening(timestamp: datetime) -> bool:
    return get_time_category(timestamp.hour) == TimeCategory.EARLY_EVENING


def is_late_evening(timestamp: datetime) -> bool:
    return get_time_category(timestamp.hour) == TimeCategory.LATE_EVENING
