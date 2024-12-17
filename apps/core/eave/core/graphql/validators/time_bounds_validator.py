from datetime import datetime, timedelta
import enum
from zoneinfo import ZoneInfo

import strawberry

from eave.stdlib.time import LOS_ANGELES_TIMEZONE

"""
Ensure an event start time is within the bounds of when
we can safely book events for a user.
"""

def start_time_too_soon(*, start_time: datetime, timezone: ZoneInfo) -> bool:
    return datetime.now(tz=timezone) + timedelta(hours=24) > start_time.astimezone(timezone)

def start_time_too_far_away(*, start_time: datetime, timezone: ZoneInfo) -> bool:
    return datetime.now(tz=timezone) + timedelta(days=30) < start_time.astimezone(timezone)
