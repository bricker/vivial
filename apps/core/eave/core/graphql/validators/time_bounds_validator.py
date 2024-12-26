from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

"""
Ensure an event start time is within the bounds of when
we can safely book events for a user.
"""


def start_time_too_soon(*, start_time: datetime, timezone: ZoneInfo) -> bool:
    return datetime.now(tz=timezone) + timedelta(hours=24) > start_time.astimezone(timezone)
