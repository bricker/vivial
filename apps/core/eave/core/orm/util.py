from datetime import datetime, timedelta

from sqlalchemy import text

PG_UUID_EXPR = text("(gen_random_uuid())")

PG_EMPTY_ARRAY_EXPR = text("'{}'")


class StartTimeTooSoonError(Exception):
    pass


class StartTimeTooLateError(Exception):
    pass

def validate_time_within_bounds_or_exception(start_time: datetime) -> None:
    """Ensure an event start time is within the bounds of when
    we can safely book events for a user."""
    now = datetime.now()
    if start_time - now > timedelta(days=30):
        raise StartTimeTooLateError()
    if start_time - now < timedelta(hours=24):
        raise StartTimeTooSoonError()
