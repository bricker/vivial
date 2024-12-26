from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

"""
Ensure an event start time is within the bounds of when
we can safely book events for a user.
"""


def start_time_too_soon(*, start_time: datetime, timezone: ZoneInfo) -> bool:
    now = datetime.now(tz=timezone)
    start_time = start_time.astimezone(timezone)
    delta = timedelta(hours=24)

    lower_bound_incl = now + delta
    lower_bound_incl = lower_bound_incl.replace(minute=0, second=0)

    return start_time >= lower_bound_incl


def start_time_too_far_away(*, start_time: datetime, timezone: ZoneInfo) -> bool:
    now = datetime.now(tz=timezone)
    start_time = start_time.astimezone(timezone)
    delta = timedelta(days=30)

    # For upper bound, we allow up to the end of the day
    upper_bound_incl = now + delta
    upper_bound_incl = upper_bound_incl.replace(hour=23, minute=59, second=59)

    return start_time <= upper_bound_incl
