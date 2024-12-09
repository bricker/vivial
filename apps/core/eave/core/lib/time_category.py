import enum
from datetime import datetime
from zoneinfo import ZoneInfo


class TimeCategory(enum.Enum):
    EARLY_MORNING = enum.auto()
    LATE_MORNING = enum.auto()
    EARLY_AFTERNOON = enum.auto()
    LATE_AFTERNOON = enum.auto()
    EARLY_EVENING = enum.auto()
    LATE_EVENING = enum.auto()


def get_time_category(dt: datetime, tz: ZoneInfo) -> TimeCategory:
    """
    Given an hour of the day in range(24), return the "time category" for that
    day (e.g. early morning, late afternoon, early evening, etc.)

    Note that midnight - 3:59 AM is considered "late evening" in this context.
    """

    local_timestamp = dt.astimezone(tz)

    if local_timestamp.hour < 4:
        return TimeCategory.LATE_EVENING  # midnight - 3:59 AM

    if local_timestamp.hour < 9:
        return TimeCategory.EARLY_MORNING  # 4:00 AM - 8:59 AM

    if local_timestamp.hour < 12:
        return TimeCategory.LATE_MORNING  # 9:00 AM - 11:59 AM

    if local_timestamp.hour < 15:
        return TimeCategory.EARLY_AFTERNOON  # 12:00 PM - 2:59 PM

    if local_timestamp.hour < 18:
        return TimeCategory.LATE_AFTERNOON  # 3:00 PM - 5:59 PM

    if local_timestamp.hour < 21:
        return TimeCategory.EARLY_EVENING  # 6:00 PM - 8:59 PM

    return TimeCategory.LATE_EVENING  # 9:00 PM - 11:59 PM


def is_early_morning(dt: datetime, tz: ZoneInfo) -> bool:
    """
    Given a timestamp return True if time is in the early morning.
    """
    return get_time_category(dt, tz) == TimeCategory.EARLY_MORNING


def is_late_morning(dt: datetime, tz: ZoneInfo) -> bool:
    """
    Given a timestamp return True if time is in the late morning.
    """
    return get_time_category(dt, tz) == TimeCategory.LATE_MORNING


def is_early_afternoon(dt: datetime, tz: ZoneInfo) -> bool:
    """
    Given a timestamp return True if time is in the early afternoon.
    """
    return get_time_category(dt, tz) == TimeCategory.EARLY_AFTERNOON


def is_late_afternoon(dt: datetime, tz: ZoneInfo) -> bool:
    """
    Given a timestamp return True if time is in the late afternoon.
    """
    return get_time_category(dt, tz) == TimeCategory.LATE_AFTERNOON


def is_early_evening(dt: datetime, tz: ZoneInfo) -> bool:
    """
    Given a timestamp return True if time is in the early evening.
    """
    return get_time_category(dt, tz) == TimeCategory.EARLY_EVENING


def is_late_evening(dt: datetime, tz: ZoneInfo) -> bool:
    """
    Given a timestamp return True if time is in the late evening.
    """
    return get_time_category(dt, tz) == TimeCategory.LATE_EVENING
