from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


class StartTimeTooSoonError(Exception):
    pass


class StartTimeTooLateError(Exception):
    pass


def validate_time_within_bounds_or_exception(*, start_time: datetime, timezone: ZoneInfo) -> None:
    """Ensure an event start time is within the bounds of when
    we can safely book events for a user."""
    now = datetime.now(tz=timezone)
    start_time = start_time.astimezone(timezone)

    if start_time - now > timedelta(days=30):
        raise StartTimeTooLateError()
    if start_time - now < timedelta(hours=24):
        raise StartTimeTooSoonError()
