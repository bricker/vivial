from datetime import datetime, timedelta
import os
import time
from zoneinfo import ZoneInfo

ONE_SECOND_IN_MS = 1000
ONE_MINUTE_IN_MS = ONE_SECOND_IN_MS * 60
ONE_HOUR_IN_MS = ONE_MINUTE_IN_MS * 60
ONE_DAY_IN_MS = ONE_HOUR_IN_MS * 24
ONE_WEEK_IN_MS = ONE_DAY_IN_MS * 7
ONE_YEAR_IN_MS = ONE_DAY_IN_MS * 365

ONE_MINUTE_IN_SECONDS = 60
ONE_HOUR_IN_SECONDS = ONE_MINUTE_IN_SECONDS * 60
ONE_DAY_IN_SECONDS = ONE_HOUR_IN_SECONDS * 24
ONE_WEEK_IN_SECONDS = ONE_DAY_IN_SECONDS * 7
ONE_YEAR_IN_SECONDS = ONE_DAY_IN_SECONDS * 365

ONE_HOUR_IN_MINUTES = 60
ONE_DAY_IN_MINUTES = ONE_HOUR_IN_MINUTES * 24
ONE_WEEK_IN_MINUTES = ONE_DAY_IN_MINUTES * 7
ONE_YEAR_IN_MINUTES = ONE_DAY_IN_MINUTES * 365

LOS_ANGELES_TIMEZONE = ZoneInfo("America/Los_Angeles")


def set_utc() -> None:
    os.environ["TZ"] = "UTC"
    time.tzset()


def datetime_window(dt: datetime, *, minutes: int) -> tuple[datetime, datetime]:
    dt = dt.replace(second=0, microsecond=0)
    one_second = timedelta(seconds=1)

    lower = dt - one_second
    lower -= timedelta(minutes=lower.minute % minutes)
    lower = lower.replace(second=0)

    upper = dt + timedelta(minutes=minutes)
    upper -= timedelta(minutes=upper.minute % minutes)
    upper = upper - one_second

    return (lower, upper)
